#  SecretBiology Copyright (c) 2020
#
#  This library is part of SecretPlot project
#  (https://github.com/secretBiology/SecretPlots)
#
#  SecretChord : A simple library to plot the Chord Diagram
#  in native matplotlib framework
#
#  All basic elements

from matplotlib.patches import Wedge, Path, PathPatch
import matplotlib.pyplot as plt
from collections import OrderedDict, defaultdict
from typing import Dict


class CommonMethods:
    def __init__(self):
        self._center = None
        self._is_visible = True
        self.kwargs = {}

    @property
    def center(self):
        if self._center is None:
            self._center = (0, 0)
        return self._center

    def hide(self):
        self._is_visible = False

    def show(self):
        self._is_visible = True

    @property
    def is_visible(self):
        return self._is_visible

    def update(self, **kwargs):
        self.kwargs = {**self.kwargs, **kwargs}


class ArchData:
    def __init__(self):
        self.radius = 1
        self.start_angle = 0
        self.end_angle = 0
        self.height = 0.1
        self.kwargs = {}


class Arch(CommonMethods):
    def __init__(self, radius: float,
                 start_angle: float, end_angle: float, *,
                 height: float,
                 **kwargs):
        super().__init__()
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.kwargs = kwargs
        self.height = height

        self._wedge = None
        self._input = OrderedDict()
        self._output = OrderedDict()

    def __repr__(self):
        return f"Arch({self.start_angle},{self.end_angle})"

    @property
    def wedge(self) -> Wedge:
        if self._wedge is None:
            self._wedge = Wedge(center=self.center,
                                r=self.radius,
                                theta1=self.start_angle, theta2=self.end_angle,
                                width=self.height,
                                **self.kwargs)
        return self._wedge

    @property
    def inputs(self) -> OrderedDict:
        return self._input

    @property
    def angle(self) -> float:
        return self.end_angle - self.start_angle

    @property
    def outputs(self) -> OrderedDict:
        return self._output

    def add_input_ribbon(self, ribbon, amount):
        self._input[ribbon] = amount

    def add_output_ribbon(self, ribbon, amount):
        self._output[ribbon] = amount

    def get_order(self):
        nodes_val = list(self.inputs.values())
        nodes_val.extend(list(self.outputs.values()))
        total = sum(nodes_val)
        nodes_val = [x * self.angle / total for x in nodes_val]
        return nodes_val[:len(self.inputs)], nodes_val[len(self.inputs):]

    def get_angle(self, node, is_output):
        val_in, val_out = self.get_order()
        current = self.start_angle
        val = val_in
        val_ref = self.inputs
        if is_output:
            val_in.append(0)  # To avoid empty sum
            current += sum(val_in)
            val = val_out
            val_ref = self.outputs

        for v in val_ref:
            if v == node:
                return current, current + val[0]
            else:
                current += val[0]
                val.pop(0)

        raise AttributeError("Wrong Ribbon direction or Wrong Arch")


class Ribbon(CommonMethods):
    def __init__(self, start_arch: Arch, end_arch: Arch, *,
                 start_radius: float, end_radius: float,
                 start_margin: float, end_margin: float,
                 **kwargs):
        super().__init__()
        self.start_arch = start_arch
        self.end_arch = end_arch
        self.start_margin = start_margin
        self.end_margin = end_margin
        self.start_radius = start_radius
        self.end_radius = end_radius
        self.kwargs = kwargs
        self._patch = None

    def get_points(self, start, end, radius, margin, arch_height):
        er = radius - margin - arch_height  # Effective Radius
        w = Wedge(self.center, er, start, end)
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

    @staticmethod
    def get_path(start_loc, end_loc):
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
        return Path(verts, codes)

    @property
    def patch(self):
        if self._patch is None:
            sp1, sp2 = self.start_arch.get_angle(self, False)
            ep1, ep2 = self.end_arch.get_angle(self, True)

            sp = self.get_points(sp1, sp2, self.start_radius,
                                 self.start_margin, self.start_arch.height)

            ep = self.get_points(ep1, ep2, self.end_radius,
                                 self.end_margin, self.end_arch.height)

            pt = self.get_path(sp, ep)
            self._patch = PathPatch(pt, **self.kwargs)
        return self._patch


class Track:
    def __init__(self):
        self._arch_amounts = defaultdict(int)
        self._arch = None
        self._order = []
        self._ribbons = None
        self._data = []

        self.arch_gap_angle = 10
        self.arch_height = 0.2
        self.rotation = 0
        self.radius = 1

        self.ribbon_start_margin = 0.1
        self.ribbon_end_margin = 0.1

    def add_flow(self, data):
        self._data.append(data)
        self._arch_amounts[data[0]] += data[2]
        self._arch_amounts[data[1]] += data[2]
        if data[0] not in self._order:
            self._order.append(data[0])
        if data[1] not in self._order:
            self._order.append(data[1])

    def add_data(self, data):
        for d in data:
            self.add_flow(d)

    @property
    def order(self):
        tmp = [x for x in self._order if x in self._arch_amounts.keys()]
        for k in self._arch_amounts.keys():
            if k not in tmp:
                tmp.append(k)
        return tmp

    @order.setter
    def order(self, value: list):
        self._order = value

    @property
    def arch(self) -> Dict[str, Arch]:
        if self._arch is None:
            raise ValueError("Please use 'generate_elements' before "
                             "accessing arch")
        return self._arch

    @property
    def ribbons(self) -> Dict[str, Ribbon]:
        if self._ribbons is None:
            raise ValueError("Please use 'generate_elements' before "
                             "accessing ribbons")
        return self._ribbons

    def generate_elements(self):
        amount = []
        keys = []
        for k in self.order:
            amount.append(self._arch_amounts[k])
            keys.append(k)
        total = sum(amount)
        amount = [x * 360 / total for x in amount]
        gap_amount = self.arch_gap_angle * len(self._arch_amounts.keys())
        total = sum(amount) + gap_amount
        amount = [x * 360 / total for x in amount]
        current = self.rotation
        all_arc = {}
        for i, arc in enumerate(keys):
            all_arc[arc] = Arch(self.radius, current, current + amount[i],
                                height=self.arch_height)
            current += amount[i] + self.arch_gap_angle

        all_ribbons = {}
        for d in self._data:
            a1 = all_arc[d[0]]
            a2 = all_arc[d[1]]
            rb = Ribbon(a1, a2,
                        start_radius=self.radius,
                        end_radius=self.radius,
                        start_margin=self.ribbon_start_margin,
                        end_margin=self.ribbon_end_margin)

            r_key = f"{d}-{len(all_ribbons)}"
            a2.add_output_ribbon(rb, d[2])
            a1.add_input_ribbon(rb, d[2])
            all_ribbons[r_key] = rb

        self._arch = all_arc
        self._ribbons = all_ribbons

    def draw(self, ax: plt.Axes):
        self.generate_elements()
        for t in self.arch.values():
            ax.add_patch(t.wedge)
        for rb in self.ribbons.values():
            ax.add_patch(rb.patch)


def run():
    _, ax = plt.subplots()  # type:plt.Axes

    data = [
        ("a", "b", 4),
        ("c", "a", 2),
        ("c2", "a", 2),
    ]
    trc = Track()
    trc.add_data(data)
    trc.draw(ax)
    ax.set_aspect(1)
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_axis_off()
    plt.show()
