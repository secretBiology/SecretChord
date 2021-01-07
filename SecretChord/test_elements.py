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
from matplotlib.text import Annotation
import matplotlib.pyplot as plt
from collections import OrderedDict, defaultdict
from typing import Dict
from SecretColors import Palette
import numpy as np


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
        self._start_radius = start_radius
        self._end_radius = end_radius
        self.kwargs = kwargs
        self._patch = None

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

    @property
    def radius(self):
        if self._radius is None:
            return self.arch.radius * 1.02
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

    def ha(self, x):
        if self._ha is not None:
            return self._ha
        return {-1: "right", 1: "left", 0: "center"}[int(np.sign(x))]

    def va(self, y):
        if self._va is not None:
            return self._va
        return "center"

    def rotation(self):
        if not self.rotate:
            return None
        if self._angle is not None:
            return self._angle
        if 180 > self.angle >= 90:
            return -abs(180 - self.angle)
        elif 270 > self.angle >= 180:
            return abs(180 - self.angle)
        return self.angle

    def get_xy(self):
        x = np.cos(np.deg2rad(self.angle)) * self.radius
        y = np.sin(np.deg2rad(self.angle)) * self.radius
        return x, y

    @staticmethod
    def get_connection_style(angle):
        return f"angle,angleA=0,angleB={angle}"

    def get_arrow_props(self):
        if not self.add_arrow:
            return {}
        return {
            "connectionstyle": self.get_connection_style(self.angle),
            "arrowstyle": self.arrowstyle}

    def _regular(self):
        x, y = self.get_xy()
        kw = {"ha": self.ha(x), "va": self.va(y),
              "rotation_mode": self.rotation_mode,
              "rotation": self.rotation(),
              }
        kw = {**kw, **self.kwargs}
        self._annotation = Annotation(self.text,
                                      xy=(x, y),
                                      **kw)

    def _with_arrow(self):
        x, y = self.get_xy()
        kw = {"ha": self.ha(x), "va": "center",
              "rotation_mode": self.rotation_mode,
              "arrowprops": self.get_arrow_props()}
        kw = {**kw, **self.kwargs}
        t_x = self.arrow_label_x_factor * self.arch.radius * np.sign(x)
        t_y = self.arrow_label_y_factor * y
        self._annotation = Annotation(self.text,
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


class Track:
    def __init__(self):
        self._arch_amounts = defaultdict(int)
        self._arch = None
        self._order = []
        self._ribbons = None
        self._arch_labels = None
        self._data = []
        self._arch_colors = None

        self.arch_gap_angle = 10
        self.arch_height = 0.1
        self.arch_alpha = 1
        self.arch_kwargs = {}

        self.rotation = 0
        self.radius = 1

        self.hide_ribbons = False
        self.hide_arch_labels = False

        self.ribbon_start_margin = 0.1
        self.ribbon_end_margin = 0.1
        self.ribbon_color_from_source = True
        self.ribbon_alpha = 0.6
        self.ribbon_kwargs = {}

        self.arch_label_arrows = False
        self.arch_label_rotate = True
        self.arch_label_kwargs = {}

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

    @property
    def arch_labels(self) -> Dict[str, ArchLabel]:
        if self._arch_labels is None:
            raise ValueError("Please use 'generate_elements' before "
                             "accessing arch_labels")
        return self._arch_labels

    @property
    def arch_colors(self):
        if self._arch_colors is None:
            self._arch_colors = {}
        return self._arch_colors

    @arch_colors.setter
    def arch_colors(self, color_dictionary: dict):
        self._arch_colors = color_dictionary

    def generate_elements(self):
        amount = []
        keys = []
        for k in self.order:
            amount.append(self._arch_amounts[k])
            keys.append(k)
        total = sum(amount)
        gap_amount = self.arch_gap_angle * len(self._arch_amounts.keys())

        if gap_amount >= 360:
            raise ValueError(f"Total Gap amount exceeded 360 degrees, "
                             f"please reduce the 'arch_gap_angle'. Current "
                             f"gap amount is {self.arch_gap_angle}")

        available_angle = 360 - gap_amount
        amount = [x * available_angle / total for x in amount]

        current = self.rotation
        all_arc = {}
        all_arch_labels = {}
        all_ribbons = {}

        cc = Palette().cycle()

        for i, arc in enumerate(keys):
            if arc not in self.arch_colors:
                self._arch_colors[arc] = next(cc)
            kwa = {"fc": self.arch_colors[arc], "alpha": self.arch_alpha}
            kwa = {**kwa, **self.arch_kwargs}
            all_arc[arc] = Arch(self.radius, current, current + amount[i],
                                height=self.arch_height, **kwa)
            arl = ArchLabel(arc, all_arc[arc])
            arl.add_arrow = self.arch_label_arrows
            arl.rotate = self.arch_label_rotate
            arl.update(**self.arch_label_kwargs)
            all_arch_labels[arc] = arl
            current += amount[i] + self.arch_gap_angle
            if current >= 360:
                current = current % 360

        for d in self._data:
            a1 = all_arc[d[0]]
            a2 = all_arc[d[1]]
            color_key = d[0]
            if not self.ribbon_color_from_source:
                color_key = d[1]
            kwr = {"fc": self.arch_colors[color_key],
                   "alpha": self.ribbon_alpha}
            kwr = {**kwr, **self.ribbon_kwargs}
            rb = Ribbon(a1, a2,
                        start_radius=None,
                        end_radius=None,
                        start_margin=self.ribbon_start_margin,
                        end_margin=self.ribbon_end_margin, **kwr)

            r_key = f"{d}-{len(all_ribbons)}"
            a2.add_output_ribbon(rb, d[2])
            a1.add_input_ribbon(rb, d[2])
            all_ribbons[r_key] = rb

        self._arch = all_arc
        self._ribbons = all_ribbons
        self._arch_labels = all_arch_labels

    def get_arch(self, key) -> Arch:
        if self._arch is None:
            self.generate_elements()
        return self.arch[key]

    def get_ribbon(self, data_entry, index) -> Ribbon:
        if self._ribbons is None:
            self.generate_elements()
        key = f"{data_entry}-{index}"
        return self.ribbons[key]

    def get_arch_label(self, key) -> ArchLabel:
        if self._arch_labels is None:
            self.generate_elements()
        return self.arch_labels[key]

    def update_arch(self, **kwargs):
        self.arch_kwargs = {**self.arch_kwargs, **kwargs}

    def update_ribbons(self, **kwargs):
        self.ribbon_kwargs = {**self.ribbon_kwargs, **kwargs}

    def update_arch_labels(self, **kwargs):
        self.arch_label_kwargs = {**self.arch_label_kwargs, **kwargs}

    def draw(self, ax: plt.Axes):
        if self._arch is None:
            self.generate_elements()
        for t in self.arch.values():
            if t.is_visible:
                ax.add_patch(t.wedge)
        if not self.hide_ribbons:
            for rb in self.ribbons.values():
                if rb.is_visible:
                    ax.add_patch(rb.patch)
        if not self.hide_arch_labels:
            for al in self.arch_labels.values():
                if al.is_visible:
                    ax.add_artist(al.annotation)


def run():
    _, ax = plt.subplots()  # type:plt.Axes

    data = [
        ("ta", "b", 4),
        ("a", "b", 4),
        ("a", "yb", 40),
        ("c", "a", 2),
        ("c2", "a", 20),
    ]
    trc = Track()
    trc.add_data(data)
    trc.draw(ax)
    ax.set_aspect(1)
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.axhline(0)
    ax.axvline(0)
    ax.set_axis_off()
    plt.show()
