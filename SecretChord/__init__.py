#  SecretBiology Copyright (c) 2020
#
#  This library is part of SecretPlot project
#  (https://github.com/secretBiology/SecretPlots)
#
#  SecretChord : A simple library to plot the Chord Diagram
#  in native matplotlib framework

import matplotlib.pyplot as plt
from SecretColors import Palette

from SecretChord._base import Track, Arch, ArchLabel, Ribbon


class ChordDiagram:
    def __init__(self, data):
        self.data = data
        self._track = None

    @property
    def track(self) -> Track:
        if self._track is None:
            trc = Track()
            trc.add_data(self.data)
            self._track = trc
        return self._track

    def arch(self, key) -> Arch:
        return self.track.get_arch(key)

    def ribbon(self, data_entry: tuple, index: int) -> Ribbon:
        return self.track.get_ribbon(data_entry, index)

    def arch_label(self, key) -> ArchLabel:
        return self.track.get_arch_label(key)

    def update_arch(self, **kwargs):
        self.track.update_arch(**kwargs)

    def update_ribbons(self, **kwargs):
        self.track.update_ribbons(**kwargs)

    def update_arch_labels(self, **kwargs):
        self.track.update_arch_labels(**kwargs)

    def fade_all(self, background_alpha=0.3):
        self.update_arch(alpha=background_alpha)
        self.update_ribbons(alpha=background_alpha, ec="None")
        self.update_arch_labels(alpha=background_alpha)

    def highlight_arch(self, key, fade: bool = True, background_alpha=0.3):
        if fade:
            self.fade_all(background_alpha)
        self.arch(key).update(alpha=1)
        self.arch_label(key).update(alpha=1)

    def highlight_ribbon(self, data_entry: tuple, index: int,
                         fade: bool = True,
                         background_alpha=0.3):
        if fade:
            self.fade_all(background_alpha)
        self.ribbon(data_entry, index).update(alpha=1)
        self.arch_label(data_entry[0]).update(alpha=1)
        self.arch_label(data_entry[1]).update(alpha=1)

    def highlight_flow(self, data_entry: tuple, index: int,
                       fade: bool = True,
                       background_alpha: float = 0.3):
        if fade:
            self.fade_all(background_alpha)
        self.ribbon(data_entry, index).update(alpha=1)
        self.arch(data_entry[0]).update(alpha=1)
        self.arch(data_entry[1]).update(alpha=1)
        self.arch_label(data_entry[0]).update(alpha=1)
        self.arch_label(data_entry[1]).update(alpha=1)

    def highlight_elements(self, key, fade: bool = True, background_alpha=0.3):
        if fade:
            self.fade_all(background_alpha)
        self.arch(key).update(alpha=1)
        for i, d in enumerate(self.data):
            if d[0] == key or d[1] == key:
                self.ribbon(d, i).update(alpha=1)
                self.arch_label(d[0]).update(alpha=1)
                self.arch_label(d[1]).update(alpha=1)

    def draw(self, ax: plt.Axes = None, pad_factor=1.2):
        if ax is None:
            _, ax = plt.subplots()

        self.track.draw(ax)

        ax.set_aspect(1)
        x_min = self.track.center[0] - self.track.radius
        x_max = self.track.center[0] + self.track.radius
        y_min = self.track.center[1] - self.track.radius
        y_max = self.track.center[1] + self.track.radius
        ax.set_xlim(x_min * pad_factor, x_max * pad_factor)
        ax.set_ylim(y_min * pad_factor, y_max * pad_factor)

        return ax


class SplitChordDiagram:
    def __init__(self, data):
        self.data = data
        self.start_center = (0, 0.5)
        self.end_center = (0, -0.5)
        self.bend_center = (0, 0)
        self.rotation = 0
        self._track = None

    @property
    def track(self) -> Track:
        if self._track is None:
            self.generate_elements()
        return self._track

    def generate_elements(self):
        cc = Palette().cycle()
        t1 = Track()
        source = [(f"{x[0]}_s", f"{x[1]}_d", x[2]) for x in self.data]
        text_map = {}
        color_map = {}
        for d in self.data:
            text_map[f"{d[0]}_s"] = d[0]
            text_map[f"{d[1]}_d"] = d[1]
            if f"{d[0]}_s" not in color_map:
                c = next(cc)
                color_map[f"{d[0]}_s"] = c
                color_map[f"{d[0]}_d"] = c
            if f"{d[1]}_s" not in color_map:
                c = next(cc)
                color_map[f"{d[1]}_s"] = c
                color_map[f"{d[1]}_d"] = c
        t1.add_data(source)
        t1.arch_colors = color_map
        t1.map_arch_labels(text_map)
        source_order = [x[0] for x in source]
        source_order = sorted(list(set(source_order)))
        t1.order = source_order
        self._track = t1

    def draw(self, ax: plt.Axes = None, pad_factor=1.2) -> plt.Axes:
        if ax is None:
            _, ax = plt.subplots()

        self.track.center = self.start_center
        self.track.rotation = self.rotation

        self.track.generate_elements()
        for a in self.track.arch:
            if a.endswith("_d"):
                self.track.get_arch(a).center = self.end_center

        source = [(f"{x[0]}_s", f"{x[1]}_d", x[2]) for x in self.data]
        for i, s in enumerate(source):
            if s[1].endswith("_d"):
                self.track.get_ribbon(s, i).bend_center = self.bend_center

        self.track.draw(ax)

        ax.set_aspect(1)
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-2, 2)
        return ax
