#  SecretBiology Copyright (c) 2020
#
#  This library is part of SecretPlot project
#  (https://github.com/secretBiology/SecretPlots)
#
#  SecretChord : A simple library to plot the Chord Diagram
#  in native matplotlib framework
#

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Wedge, Path, PathPatch


class CommonElements:
    def __init__(self, radius: float = None,
                 width: float = None, ):
        self._radius = None
        self._width = None
        self._center = None
        self._is_hidden = False

    @property
    def radius(self):
        if self._radius is None:
            self._radius = 1
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

    def hide(self):
        self._is_hidden = True

    def show(self):
        self._is_hidden = False

    @property
    def is_hidden(self):
        return self._is_hidden


class Arch(CommonElements):
    def __init__(self, start: float, end: float, **kwargs):
        super().__init__()
        self.start = start
        self.end = end
        self.kwargs = kwargs
        self._wedge = None
        self._current = 0

    def update(self, **kwargs):
        self.kwargs = {**self.kwargs, **kwargs}

    def color(self, value):
        self.update(facecolor=value)

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

    def update_usage(self, used):
        self._current += used

    def draw(self, ax: plt.Axes):
        if self.is_hidden:
            return
        w = Wedge(self.center, self.radius, self.start, self.end, self.width,
                  **self.kwargs)
        w = ax.add_patch(w)
        self._wedge = w


class Ribbon(CommonElements):
    def __init__(self, start1: float, start2: float,
                 end1: float, end2: float,
                 gap_start: float, gap_end: float,
                 radius_start: float, radius_end: float,
                 **kwargs):
        super().__init__()
        self.start1 = start1
        self.start2 = start2
        self.end1 = end1
        self.end2 = end2
        self.gap_start = gap_start
        self.gap_end = gap_end
        self.radius_start = radius_start
        self.radius_end = radius_end
        self.kwargs = kwargs
        self._gap = None
        self._path = None

    def update(self, **kwargs):
        self.kwargs = {**self.kwargs, **kwargs}

    def color(self, value):
        self.update(facecolor=value)

    @property
    def gap(self):
        if self._gap is None:
            self._gap = 0.1
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

    def adjust_radia(self, new_radius, new_width):
        if new_radius - new_width < self.radius_start - self.gap:
            self.radius_start = new_radius - new_width - self.gap

        if new_radius - new_width < self.radius_end - self.gap:
            self.radius_end = new_radius - new_width - self.gap

    def get_points(self, start, end, gap, radius):
        w = Wedge(self.center, radius - gap - self.gap,
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
        if self.is_hidden:
            return
        start_loc = self.get_points(self.start1, self.start2,
                                    self.gap_start, self.radius_start)
        end_loc = self.get_points(self.end1, self.end2, self.gap_end,
                                  self.radius_end)
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
    def __init__(self, arch1: Arch, arch2: Arch,
                 start_fraction: float, end_fraction: float,
                 **kwargs):
        self.arch1 = arch1
        self.arch2 = arch2
        self.start_fraction = start_fraction
        self.end_fraction = end_fraction
        self.margin_start = 0.3
        self.margin_end = 0.3
        self.kwargs = kwargs
        self._ribbon = None

    @staticmethod
    def get_angles(a: Arch, used):
        s1 = a.start + a.available_angle * a.used
        s2 = s1 + a.angle(used)
        a.update_usage(used)
        return s1, s2

    @property
    def ribbon(self) -> Ribbon:
        if self._ribbon is None:
            s1, s2 = self.get_angles(self.arch1, self.start_fraction)
            e1, e2 = self.get_angles(self.arch2, self.end_fraction)

            self._ribbon = Ribbon(s1, s2, e1, e2,
                                  self.margin_start, self.margin_end,
                                  self.arch1.radius, self.arch2.radius,
                                  **self.kwargs)
        return self._ribbon

    def draw(self, ax: plt.Axes):
        self.ribbon.draw(ax)


class Label:
    def __init__(self, arch_id: str, archs: Arch, **kwargs):
        self.arch_id = arch_id
        self.arch = arch
        self.gap = 1.05
        self.rotate = True

        self.add_arrow = False
        self.arrowstyle = "->"
        self.arrow_label_x_factor = 1.2
        self.arrow_label_y_factor = 1.2
        self.kwargs = kwargs

        self._is_hidden = False
        self._text = None
        self._ha = None
        self._va = None
        self._angle = None

    def update(self, **kwargs):
        self.kwargs = {**self.kwargs, **kwargs}

    @property
    def text(self):
        if self._text is None:
            return self.arch_id
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    @property
    def is_hidden(self):
        return self._is_hidden

    def hide(self):
        self._is_hidden = True

    def show(self):
        self._is_hidden = False

    def get_xy(self, angle):
        x = np.cos(np.deg2rad(angle)) * (self.arch.radius * self.gap)
        y = np.sin(np.deg2rad(angle)) * (self.arch.radius * self.gap)
        return x, y

    def ha(self, x):
        if self._ha is not None:
            return self._ha
        return {-1: "right", 1: "left", 0: "center"}[int(np.sign(x))]

    def va(self, y):
        if self._va is not None:
            return self._va
        return {-1: "top", 1: "bottom", 0: "center"}[int(np.sign(y))]

    def rotation(self, angle):
        if not self.rotate:
            return None
        if self._angle is not None:
            return self._angle
        if 180 > angle >= 90:
            return -abs(180 - angle)
        elif 270 > angle >= 180:
            return abs(180 - angle)
        return angle

    @staticmethod
    def get_connection_style(angle):
        return f"angle,angleA=0,angleB={angle}"

    def get_arrow_props(self, angle):
        if not self.add_arrow:
            return {}
        return {
            "connectionstyle": self.get_connection_style(angle),
            "arrowstyle": self.arrowstyle}

    def _draw_regular(self, ax, x, y, ang):
        kw = {"ha": self.ha(x), "va": self.va(y),
              "rotation": self.rotation(ang)}
        kw = {**kw, **self.kwargs}
        ax.annotate(self.text,
                    xy=(x, y), **kw)

    def _draw_arrow(self, ax, x, y, ang):
        kw = {"ha": self.ha(x), "va": "center",
              "arrowprops": self.get_arrow_props(ang)}
        kw = {**kw, **self.kwargs}
        ax.annotate(self.text,
                    xy=(x, y),
                    xytext=(
                        self.arrow_label_x_factor * self.arch.radius * np.sign(
                            x),
                        self.arrow_label_y_factor * y
                    ), **kw)

    def draw(self, ax: plt.Axes):
        if self.is_hidden:
            return
        ang = self.arch.start + (self.arch.end - self.arch.start) / 2
        x, y = self.get_xy(ang)

        if self.add_arrow:
            self._draw_arrow(ax, x, y, ang)
        else:
            self._draw_regular(ax, x, y, ang)
