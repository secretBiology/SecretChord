#  SecretBiology Copyright (c) 2020
#
#  This library is part of SecretPlot project
#  (https://github.com/secretBiology/SecretPlots)
#
#  SecretChord : A simple library to plot the Chord Diagram
#  in native matplotlib framework
#
#  Basic Assembler

from collections import defaultdict
from typing import Dict

import matplotlib.pyplot as plt
from SecretColors import Palette
from SecretChord._elements import Flow, Arch, Label


class Assembler:
    def __init__(self, data: list):
        self.data = data

        self._gap = None
        self._amount = None
        self._no_of_ribbons = None
        self._start_angle = None
        self._end_angle = None
        self._arch = None
        self._flows = None
        self._colors = None
        self._arch_order = None
        self._labels = None

        self.rotation = 0
        self.reverse_color = False
        self.radius = None
        self.order = None
        self.ribbon_alpha = 0.6
        self.arch_alpha = 1
        self.margin_start = 0.3
        self.margin_end = 0.3

    @property
    def gap(self) -> float:
        if self._gap is None:
            self._gap = 0.1
        return self._gap

    @gap.setter
    def gap(self, value: float):
        self._gap = value

    @property
    def colors(self) -> dict:
        if self._colors is None:
            p = Palette()
            if len(p.get_color_list) <= len(self.amount):
                self._colors = {x1: x2 for x1, x2 in
                                zip(self.arch_order,
                                    p.random(no_of_colors=len(self.amount)))}
            else:
                self._colors = {x1: x2 for x1, x2 in
                                zip(self.arch_order,
                                    p.get_color_list[:len(self.amount)])}
        return self._colors

    def map_colors(self, mapping: dict):
        for k, v in mapping.items():
            if k in self.colors:
                self._colors[k] = v

    def _generate_amount(self):
        k = defaultdict(list)
        for d in self.data:
            k[d[0]].append(d[2])
            k[d[1]].append(d[2])
        self._no_of_ribbons = {m: len(n) for m, n in k.items()}
        self._amount = {m: sum(n) for m, n in k.items()}
        if self.order is None:
            self._arch_order = [x for x in k.keys()]
        else:
            self._arch_order = [x for x in self.order if x in k.keys()]
            tmp = [x for x in k.keys() if x not in self.order]
            self._arch_order.extend(tmp)

    @property
    def amount(self) -> dict:
        if self._amount is None:
            self._generate_amount()
        return self._amount

    @property
    def arch_order(self) -> list:
        if self._arch_order is None:
            self._generate_amount()
        return self._arch_order

    @property
    def no_of_ribbons(self) -> dict:
        if self._no_of_ribbons is None:
            self._generate_amount()
        return self._no_of_ribbons

    def regenerate_angles(self):
        self._start_angle = None
        self._end_angle = None
        for k, a in self.arch.items():
            a.start = self.arch_start[k]
            a.end = self.arch_end[k]

    def regenerate_radius(self):
        for a in self.arch.values():
            a.radius = self.radius

    def _generate_angles(self):
        if self._start_angle is None or self._end_angle is None:
            gp = self.gap * len(self.amount)
            total = gp + sum(self.amount.values())
            agl_start = {}
            agl_end = {}
            current = self.rotation
            gp = self.gap * 360 / total
            for k in self.arch_order:
                agl_start[k] = current
                current += (self.amount[k] * 360 / total)
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
            for k in self.arch_order:
                kw = {"facecolor": self.colors[k], "alpha": self.arch_alpha}
                a = Arch(self.arch_start[k],
                         self.arch_end[k], **kw)
                a.radius = self.radius
                tk[k] = a
            self._arch = tk
        return self._arch

    def get_key(self, data_entry):
        return f"{data_entry[0]}-{data_entry[1]}-{data_entry[2]}-" \
               f"{self.data.index(data_entry)}"

    def get_flow(self, data_entry) -> Flow:
        return self.flows[self.get_key(data_entry)]

    @property
    def flows(self):
        if self._flows is None:
            rb = {}
            for d in self.data:
                dir_key = d[0]
                if self.reverse_color:
                    dir_key = d[1]

                start = self.arch[d[0]]
                end = self.arch[d[1]]
                s_total = self.amount[d[0]]
                e_total = self.amount[d[1]]
                start_frac = d[2] / s_total
                end_frac = d[2] / e_total
                key = f"{d[0]}-{d[1]}-{d[2]}-{len(rb)}"
                kw = {"facecolor": self.colors[dir_key],
                      "alpha": self.ribbon_alpha}
                f = Flow(start, end, start_frac, end_frac, **kw)
                f.margin_start = self.margin_start
                f.margin_end = self.margin_end
                rb[key] = f
            self._flows = rb
        return self._flows

    @property
    def labels(self):
        if self._labels is None:
            tk = {}
            for a in self.arch:
                tk[a] = Label(a, self.arch[a])
            self._labels = tk
        return self._labels

    def draw(self, ax: plt.Axes):
        for a in self.arch.values():
            a.draw(ax)
        for rb in self.flows.values():
            rb.draw(ax)
        for tx in self.labels.values():
            tx.draw(ax)
