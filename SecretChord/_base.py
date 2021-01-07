#  SecretBiology Copyright (c) 2020
#
#  This library is part of SecretPlot project
#  (https://github.com/secretBiology/SecretPlots)
#
#  SecretChord : A simple library to plot the Chord Diagram
#  in native matplotlib framework
#
#  All basic elements

from collections import defaultdict
from typing import Dict

import matplotlib.pyplot as plt
from SecretColors import Palette

from SecretChord._elements import *


class Track:
    def __init__(self):
        self._arch_amounts = defaultdict(int)
        self._arch = None
        self._order = []
        self._ribbons = None
        self._arch_labels = None
        self._data = []
        self._arch_colors = None

        self.arch_gap_angle = 5
        self.arch_height = 0.1
        self.arch_alpha = 1
        self.arch_kwargs = {}

        self.rotation = 0
        self._radius = 1
        self.center = (0, 0)
        self.max_angle = 360

        self.hide_ribbons = False
        self.hide_arch_labels = False

        self.ribbon_start_margin = 0.05
        self.ribbon_end_margin = 0.05
        self.ribbon_color_from_source = True
        self.ribbon_alpha = 0.6
        self.ribbon_kwargs = {}

        self.arch_label_arrows = False
        self.arch_label_rotate = True
        self.arch_label_colored = False
        self.arch_label_gap = 0.02
        self.arch_label_wrap_words = np.inf
        self.arch_label_kwargs = {}
        self._arch_label_mapping = {}

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value: float):
        self._radius = value

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

        if gap_amount >= self.max_angle:
            raise ValueError(
                f"Total Gap amount exceeded 'max_angle' ({self.max_angle} "
                f"degrees), please reduce the 'arch_gap_angle'. Current "
                f"gap amount is {self.arch_gap_angle}")

        available_angle = self.max_angle - gap_amount
        amount = [x * available_angle / total for x in amount]

        current = self.rotation
        all_arc = {}
        all_arch_labels = {}
        all_ribbons = {}

        cc = Palette().cycle()

        for i, arc in enumerate(keys):
            # Arch
            if arc not in self.arch_colors:
                self._arch_colors[arc] = next(cc)
            kwa = {"fc": self.arch_colors[arc], "alpha": self.arch_alpha}
            kwa = {**kwa, **self.arch_kwargs}
            a = Arch(self.radius, current, current + amount[i],
                     height=self.arch_height, **kwa)
            a.center = self.center
            all_arc[arc] = a
            # Labels
            arl = ArchLabel(arc, all_arc[arc])
            arl.add_arrow = self.arch_label_arrows
            arl.rotate = self.arch_label_rotate
            arl.wrap_words = self.arch_label_wrap_words
            arl.label_gap = self.arch_label_gap
            arl.center = self.center
            if arc in self._arch_label_mapping:
                arl.text = self._arch_label_mapping[arc]
            if self.arch_label_colored:
                arl.update(color=self.arch_colors[arc])
            arl.update(**self.arch_label_kwargs)
            all_arch_labels[arc] = arl
            current += amount[i] + self.arch_gap_angle
            if current >= 360:
                current = current % 360

        # Ribbons
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

            rb.center = self.center

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

    def map_arch_labels(self, mapping_dictionary: dict):
        self._arch_label_mapping = mapping_dictionary

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
