#  SecretBiology Copyright (c) 2020
#
#  This library is part of SecretPlot project
#  (https://github.com/secretBiology/SecretPlots)
#
#  SecretChord : A simple library to plot the Chord Diagram
#  in native matplotlib framework

import matplotlib.pyplot as plt

from SecretChord._base import Assembler


class ChordDiagram:
    def __init__(self, data: list):
        self.data = data
        self._assembler = None

        self._radius = 2
        self.rotation = 0
        self.reverse_color = False

        self._arch_gap = None
        self._arch_height = 0.3
        self.arch_order = None
        self.arch_alpha = 1

        self.ribbon_margin_start = 0.3
        self.ribbon_margin_end = 0.3
        self.ribbon_alpha = 0.6

        self._label_hide = False
        self.label_rotate = True
        self.label_color = False
        self.label_alpha = 1
        self.label_add_arrow = False

    @property
    def graph(self) -> Assembler:
        if self._assembler is None:
            self._assembler = Assembler(self.data)
        return self._assembler

    def update(self, name, value):
        setattr(self, name, value)

    def _adjust(self):
        self.graph.reverse_color = self.reverse_color
        self.graph.order = self.arch_order
        self.graph.rotation = self.rotation
        self.graph.margin_start = self.ribbon_margin_start
        self.graph.margin_end = self.ribbon_margin_end
        self.graph.arch_alpha = self.arch_alpha
        self.graph.ribbon_alpha = self.ribbon_alpha
        self._update_text()

    def _update_text(self):
        for lb in self.graph.labels.values():
            lb.rotate = self.label_rotate
            lb.add_arrow = self.label_add_arrow
            lb.update(alpha=self.label_alpha)
            if self.label_color:
                lb.update(color=self.graph.colors[lb.arch_id])

    @property
    def label_hide(self):
        return self._label_hide

    @property
    def arch_gap(self):
        return self._arch_gap

    @property
    def radius(self):
        return self._radius

    @property
    def arch_height(self):
        return self._arch_height

    @arch_height.setter
    def arch_height(self, value: float):
        self._arch_height = value
        for a in self.graph.arch.values():
            a.width = value

    @radius.setter
    def radius(self, value: float):
        self._radius = value
        self.graph.radius = value
        self.graph.regenerate_radius()

    @arch_gap.setter
    def arch_gap(self, value):
        self._arch_gap = value
        self.graph.gap = value
        self.graph.regenerate_angles()

    @label_hide.setter
    def label_hide(self, value: bool):
        for lb in self.graph.labels.values():
            if value:
                lb.hide()
            else:
                lb.show()

    def rotate(self, angle):
        self.rotation = angle

    def arch(self, key):
        return self.graph.arch[key]

    def flow(self, data_entry):
        return self.graph.get_flow(data_entry)

    def ribbon(self, data_entry):
        return self.graph.get_flow(data_entry).ribbon

    def label(self, key):
        return self.graph.labels[key]

    def update_arch(self, **kwargs):
        for a in self.graph.arch.values():
            a.update(**kwargs)

    def update_ribbons(self, **kwargs):
        for rb in self.graph.flows.values():
            rb.ribbon.update(**kwargs)

    def update_labels(self, **kwargs):
        for lb in self.graph.labels.values():
            lb.update(**kwargs)

    def fade_all(self, arch_alpha=0.2, ribbon_alpha=0.2):
        self.update_arch(alpha=arch_alpha)
        self.update_ribbons(alpha=ribbon_alpha)

    def highlight_flow(self, start: str, end: str,
                       arch_alpha=0.2, ribbon_alpha=0.2):
        self.fade_all(arch_alpha, ribbon_alpha)
        for d in self.data:
            if d[0] == start and d[1] == end:
                self.arch(start).update(alpha=1)
                self.arch(end).update(alpha=1)
                self.ribbon(d).update(alpha=1)

    def highlight_source(self, arch: str,
                         arch_alpha=0.2, ribbon_alpha=0.2):
        self.fade_all(arch_alpha, ribbon_alpha)
        self.arch(arch).update(alpha=1)
        for d in self.data:
            if d[0] == arch:
                self.ribbon(d).update(alpha=1)

    def highlight_arch(self, arch: str,
                       arch_alpha=0.2, ribbon_alpha=0.2):
        self.fade_all(arch_alpha, ribbon_alpha)
        self.arch(arch).update(alpha=1)

    def highlight_target(self, arch: str,
                         arch_alpha=0.2, ribbon_alpha=0.2):
        self.fade_all(arch_alpha, ribbon_alpha)
        self.arch(arch).update(alpha=1)
        for d in self.data:
            if d[1] == arch:
                self.ribbon(d).update(alpha=1)

    def color_mapping(self, colors: dict):
        for k, a in self.graph.arch.items():
            if k in colors.keys():
                a.update(facecolor=colors[k])
                ind = 0
                if self.reverse_color:
                    ind = 1
                for d in self.data:
                    if d[ind] == k:
                        self.ribbon(d).update(facecolor=colors[k])

    def label_mapping(self, labels: dict):
        for k, lb in self.graph.labels.items():
            if k in labels.keys():
                lb.text = labels[k]

    def draw(self, ax: plt.Axes = None) -> plt.Axes:
        if ax is None:
            _, ax = plt.subplots()

        self._adjust()
        self.graph.draw(ax)
        ax.set_aspect(1)
        ax.set_xlim(self.radius * -1.2, self.radius * 1.2)
        ax.set_ylim(self.radius * -1.2, self.radius * 1.2)
        ax.set_axis_off()
        return ax


def run():
    data = [
        ("a", "b", 2),
        ("d", "c", 5),
        ("c", "b", 5),
        ("c", "fc", 10),
        ("2sdf", "fc", 5),
    ]
    cd = ChordDiagram(data)
    cd.radius = 10
    cd.arch_gap = 2
    cd.arch_height = 2
    cd.draw()
    plt.tight_layout()
    plt.show()
