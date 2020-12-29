#  SecretBiology Copyright (c) 2020
#
#  This library is part of SecretPlot project
#  (https://github.com/secretBiology/SecretPlots)
#
#  SecretChord : A simple library to plot the Chord Diagram
#  in native matplotlib framework
#

import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Path, PathPatch
from collections import defaultdict
from typing import Dict


class CommonElements:
    def __init__(self, radius: float = None,
                 width: float = None, ):
        self._radius = None
        self._width = None
        self._center = None

    @property
    def radius(self):
        if self._radius is None:
            self._radius = 2
        return self._radius

    @radius.setter
    def radius(self, value: float):
        self._radius = value

    @property
    def center(self):
        if self._center is None:
            self._center = (0, 0)
        return self._center

    @property
    def width(self):
        if self._width is None:
            self._width = 0.3
        return self._width

    @width.setter
    def width(self, value: float):
        self._width = value


class Arch(CommonElements):
    def __init__(self, start: float, end: float, **kwargs):
        super().__init__()
        self.start = start
        self.end = end
        self.kwargs = kwargs
        self._wedge = None
        self._current = 0
        self.ribbon_gap = 0.05

    def __repr__(self):
        return f"Arch({round(self.start, 2)},{round(self.end, 2)})"

    @property
    def used(self):
        return self._current

    @property
    def available_angle(self) -> float:
        return self.end - self.start

    def angle(self, fraction: float):
        return self.available_angle * fraction

    @property
    def wedge(self) -> Wedge:
        if self._wedge is None:
            raise AttributeError(
                "You should draw the wedge before accessing it.")
        return self._wedge

    def update(self, used):
        self._current += used + self.ribbon_gap

    def draw(self, ax: plt.Axes):
        w = Wedge(self.center, self.radius, self.start, self.end, self.width,
                  **self.kwargs)
        w = ax.add_patch(w)
        self._wedge = w


class Ribbon(CommonElements):
    def __init__(self, start1: float, start2: float,
                 end1: float, end2: float,
                 gap_start: float, gap_end: float,
                 **kwargs):
        super().__init__()
        self.start1 = start1
        self.start2 = start2
        self.end1 = end1
        self.end2 = end2
        self.gap_start = gap_start
        self.gap_end = gap_end
        self.kwargs = kwargs
        self._gap = None
        self._path = None

    @property
    def gap(self):
        if self._gap is None:
            self._gap = 0.2
        return self._gap

    @gap.setter
    def gap(self, value: float):
        self._gap = value

    @property
    def path(self) -> PathPatch:
        if self._path is None:
            raise AttributeError("You should draw the ribbon before accessing "
                                 "it.")
        return self._path

    def get_points(self, start, end, gap):
        w = Wedge(self.center, self.radius - gap - self.gap,
                  start, end, self.gap)
        data = []
        first = None
        for k in w.get_path().iter_segments():
            if k[1] != 4 and len(data) > 0:
                break
            else:
                if k[1] == 4:
                    data.append(k)
                else:
                    first = k
        ap = []
        for d in data:
            points = d[0]
            points = [(points[x], points[x + 1]) for x in
                      range(0, len(points), 2)]
            ap.extend(points)
        ap.insert(0, first[0])
        return ap

    def draw(self, ax: plt.Axes):
        start_loc = self.get_points(self.start1, self.start2, self.gap_start)
        end_loc = self.get_points(self.end1, self.end2, self.gap_end)
        verts = [start_loc[0]]
        codes = [Path.MOVETO]
        for s in start_loc[1:]:
            verts.append(s)
            codes.append(Path.CURVE4)
        verts.extend([(0, 0)] * 2)
        codes.extend([Path.CURVE4] * 2)
        for e in end_loc:
            verts.append(e)
            codes.append(Path.CURVE4)
        verts.extend([(0, 0)] * 2)
        verts.append(verts[0])
        codes.extend([Path.CURVE4] * 3)
        pt = Path(verts, codes)
        pt = PathPatch(pt, **self.kwargs)
        pt = ax.add_patch(pt)
        self._path = pt


class Flow:
    def __init__(self, a1: Arch, a2: Arch,
                 start_fraction: float, end_fraction: float,
                 radius=None, **kwargs):
        self.a1 = a1
        self.a2 = a2
        self.radius = radius
        self.start_fraction = start_fraction
        self.end_fraction = end_fraction
        self.kwargs = kwargs

    @staticmethod
    def get_angles(a: Arch, used):
        s1 = a.start + a.available_angle * a.used
        s2 = s1 + a.angle(used)
        a.update(used)
        return s1, s2

    def draw(self, ax: plt.Axes):
        s1, s2 = self.get_angles(self.a1, self.start_fraction)
        e1, e2 = self.get_angles(self.a2, self.end_fraction)
        rb = Ribbon(s1, s2, e1, e2,
                    self.a1.width, self.a2.width,
                    **self.kwargs)
        rb.radius = self.radius
        rb.draw(ax)


class ChordDiagram:
    def __init__(self, data: list):
        self.data = data
        self._gap = None
        self._amount = None
        self._no_of_ribbons = None
        self._start_angle = None
        self._end_angle = None
        self._arch = None
        self.radius = None
        self._ribbons = None
        self.starting_angle = 0

    @property
    def gap(self) -> float:
        if self._gap is None:
            self._gap = 0.1
        return self._gap

    @gap.setter
    def gap(self, value: float):
        self._gap = value

    def _generate_amount(self):
        k = defaultdict(list)
        for d in self.data:
            k[d[0]].append(d[2])
            k[d[1]].append(d[2])
        self._no_of_ribbons = {m: len(n) for m, n in k.items()}
        self._amount = {m: sum(n) for m, n in k.items()}

    @property
    def amount(self) -> dict:
        if self._amount is None:
            self._generate_amount()
        return self._amount

    @property
    def no_of_ribbons(self) -> dict:
        if self._no_of_ribbons is None:
            self._generate_amount()
        return self._no_of_ribbons

    def _generate_angles(self):
        if self._start_angle is None or self._end_angle is None:
            gp = self.gap * len(self.amount)
            total = gp + sum(self.amount.values())
            agl_start = {}
            agl_end = {}
            current = self.starting_angle
            gp = self.gap * 360 / total
            for k, v in self.amount.items():
                agl_start[k] = current
                current += (v * 360 / total)
                agl_end[k] = current
                current += gp
            self._start_angle = agl_start
            self._end_angle = agl_end

    @property
    def arch_start(self) -> dict:
        if self._start_angle is None:
            self._generate_angles()
        return self._start_angle

    @property
    def arch_end(self) -> dict:
        if self._end_angle is None:
            self._generate_angles()
        return self._end_angle

    @property
    def arch(self) -> Dict[str, Arch]:
        if self._arch is None:
            tk = {}
            for k in self.amount.keys():
                a = Arch(self.arch_start[k],
                         self.arch_end[k])
                a.radius = self.radius
                tk[k] = a
            self._arch = tk
        return self._arch

    def get_key(self, data_entry):
        return f"{data_entry[0]}-{data_entry[1]}-{data_entry[2]}-" \
               f"{self.data.index(data_entry)}"

    @property
    def ribbons(self):
        if self._ribbons is None:
            rb = {}
            for d in self.data:
                start = self.arch[d[0]]
                end = self.arch[d[1]]
                sn = self.no_of_ribbons[d[0]]
                en = self.no_of_ribbons[d[1]]
                sr = start.ribbon_gap * (sn - 1) * self.amount[d[0]]
                er = end.ribbon_gap * (en - 1) * self.amount[d[1]]
                s_total = self.amount[d[0]] + sr
                e_total = self.amount[d[1]] + er
                start_frac = d[2] / s_total
                end_frac = d[2] / e_total
                key = f"{d[0]}-{d[1]}-{d[2]}-{len(rb)}"
                rb[key] = Flow(start, end, start_frac, end_frac,
                               radius=self.radius)
            self._ribbons = rb
        return self._ribbons

    def draw(self, ax: plt.Axes):
        for a in self.arch.values():
            a.draw(ax)
        for rb in self.ribbons.values():
            rb.draw(ax)


def run():
    fig, ax = plt.subplots()
    data = [
        ("a", "b", 3),
        ("b", "c", 2),
        ("a", "dd", 2),
        ("a", "u", 12),
        ("2d", "c", 10),
        ("e", "a", 2),
    ]
    cd = ChordDiagram(data)
    cd.gap = 0.8
    cd.ribbons[cd.get_key(data[5])].kwargs.update({"color": "r"})
    cd.draw(ax)
    plt.xlim(-3, 3)
    plt.ylim(-3, 3)
    ax.set_aspect(1)
    plt.show()
