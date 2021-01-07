#  SecretBiology Copyright (c) 2020
#
#  This library is part of SecretPlot project
#  (https://github.com/secretBiology/SecretPlots)
#
#  SecretChord : A simple library to plot the Chord Diagram
#  in native matplotlib framework
#

from collections import OrderedDict

import numpy as np
from matplotlib.patches import Wedge, Path, PathPatch
from matplotlib.text import Annotation


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

    @center.setter
    def center(self, value: tuple):
        self._center = value

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
        self._start_radius = start_radius
        self._end_radius = end_radius
        self.kwargs = kwargs
        self._patch = None
        self.bend_center = None

    @property
    def start_radius(self):
        if self._start_radius is None:
            return self.start_arch.radius
        return self._start_radius

    @start_radius.setter
    def start_radius(self, value: float):
        self._start_radius = value

    @property
    def end_radius(self):
        if self._end_radius is None:
            return self.end_arch.radius
        return self._end_radius

    @end_radius.setter
    def end_radius(self, value: float):
        self._end_radius = value

    def get_points(self, start, end, radius, margin, arch: Arch):
        er = radius - margin - arch.height  # Effective Radius
        w = Wedge(arch.center, er, start, end)
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

    def get_path(self, start_loc, end_loc):
        bend = self.bend_center
        if bend is None:
            bend = self.center
        verts = [start_loc[0]]
        codes = [Path.MOVETO]
        for s in start_loc[1:]:
            verts.append(s)
            codes.append(Path.CURVE4)
        verts.extend([bend] * 2)
        codes.extend([Path.CURVE4] * 2)
        for e in end_loc:
            verts.append(e)
            codes.append(Path.CURVE4)
        verts.extend([bend] * 2)
        verts.append(verts[0])
        codes.extend([Path.CURVE4] * 3)
        return Path(verts, codes)

    @property
    def patch(self):
        if self._patch is None:
            sp1, sp2 = self.start_arch.get_angle(self, False)
            ep1, ep2 = self.end_arch.get_angle(self, True)

            sp = self.get_points(sp1, sp2, self.start_radius,
                                 self.start_margin, self.start_arch)

            ep = self.get_points(ep1, ep2, self.end_radius,
                                 self.end_margin, self.end_arch)

            pt = self.get_path(sp, ep)
            self._patch = PathPatch(pt, **self.kwargs)
        return self._patch


class ArchLabel(CommonMethods):
    def __init__(self, arch_key: str, arch: Arch):
        super().__init__()

        self.arch_key = arch_key
        self.arch = arch
        self.rotate = True

        self._text = None
        self._radius = None
        self._angle = None
        self._annotation = None
        self._ha = None
        self._va = None
        self._angle = None

        self.add_arrow = False
        self.arrowstyle = "->"
        self.arrow_label_x_factor = 1.2
        self.arrow_label_y_factor = 1.2
        self.rotation_mode = "anchor"
        self.wrap_words = np.inf
        self.label_gap = 0.02

    @property
    def radius(self):
        if self._radius is None:
            return self.arch.radius + self.label_gap
        return self._radius

    @radius.setter
    def radius(self, value: float):
        self._radius = value

    @property
    def angle(self):
        if self._angle is None:
            return self.arch.start_angle + (self.arch.end_angle -
                                            self.arch.start_angle) / 2
        return self._angle

    @angle.setter
    def angle(self, value: float):
        self._angle = value

    @property
    def text(self):
        if self._text is None:
            return self.arch_key
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = value

    def ha(self, x):
        if self._ha is not None:
            return self._ha

        return {-1: "right", 1: "left", 0: "center"}[int(np.sign(
            x - self.center[0]))]

    def va(self):
        if self._va is not None:
            return self._va
        return "center"

    def rotation(self):
        if not self.rotate:
            return None
        if self._angle is not None:
            return self._angle
        if 180 > self.angle > 90:
            return -abs(180 - self.angle)
        elif 270 >= self.angle >= 180:
            return abs(180 - self.angle)
        return self.angle

    def get_xy(self):
        x = np.cos(np.deg2rad(self.angle)) * self.radius + self.arch.center[0]
        y = np.sin(np.deg2rad(self.angle)) * self.radius + self.arch.center[1]
        return x, y

    def wrapped_text(self):
        if self.wrap_words == 0:
            return self.text
        word_list = self.text.split(" ")
        adjusted_text = ""
        counter = 0
        for w in word_list:
            adjusted_text += w
            adjusted_text += " "
            counter += 1
            if counter >= self.wrap_words:
                adjusted_text = adjusted_text.strip()
                adjusted_text += "\n"
                counter = 0

        return adjusted_text.strip()

    @staticmethod
    def get_connection_style(angle):
        if angle == 180 or angle == 0:
            return "angle3"
        return f"angle,angleA=0,angleB={angle}"

    def get_arrow_props(self):
        if not self.add_arrow:
            return {}
        return {
            "connectionstyle": self.get_connection_style(self.angle),
            "arrowstyle": self.arrowstyle}

    def _regular(self):
        x, y = self.get_xy()
        kw = {"ha": self.ha(x), "va": self.va(),
              "rotation_mode": self.rotation_mode,
              "annotation_clip": False,
              "rotation": self.rotation(),
              }
        kw = {**kw, **self.kwargs}
        self._annotation = Annotation(self.wrapped_text(),
                                      xy=(x, y),
                                      **kw)

    def _with_arrow(self):
        x, y = self.get_xy()
        kw = {"ha": self.ha(x), "va": "center",
              "annotation_clip": False,
              "rotation_mode": self.rotation_mode,
              "arrowprops": self.get_arrow_props()}
        kw = {**kw, **self.kwargs}

        t_x = self.arrow_label_x_factor * self.arch.radius * np.sign(x) + \
              self.arch.center[0]
        t_y = self.arrow_label_y_factor * y + self.arch.center[1]
        self._annotation = Annotation(self.wrapped_text(),
                                      xy=(x, y),
                                      xytext=(t_x, t_y), **kw)

    @property
    def annotation(self):
        if self._annotation is None:
            if self.add_arrow:
                self._with_arrow()
            else:
                self._regular()
        return self._annotation
