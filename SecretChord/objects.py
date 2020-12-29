#  SecretBiology Copyright (c) 2020.
#  This library is part of SecretPlot project
#  (https://github.com/secretBiology/SecretPlots)
#
#  SecretChord : A simple library to plot the Chord Diagram
#  in native matplotlib framework
#
#
import numbers
import warnings
from collections import defaultdict
from typing import Union, List

import matplotlib.pyplot as plt
import numpy as np
from SecretColors import Palette
from matplotlib.patches import (Wedge, Path,
                                PathPatch)

_chord_pallet = Palette()


def _warn(msg):
    warnings.warn(msg, UserWarning)


def draw_arch(ax, start, end, width=0.2,
              radius=1.0,
              offset=0,
              color=_chord_pallet.blue(), **kwargs) -> Wedge:
    w = Wedge(center=(0, 0),
              r=radius,
              theta1=offset + start,
              theta2=offset + end,
              width=width,
              facecolor=color, **kwargs)
    ax.add_patch(w)
    return w


def _color_cycle():
    while True:
        for m in _chord_pallet.get_color_list:
            if m in [_chord_pallet.white(), _chord_pallet.black()]:
                continue
            yield m


def get_ribbon_points(radius, width, start, end) -> list:
    w = Wedge(center=(0, 0),
              r=radius,
              theta1=start,
              theta2=end,
              width=width)

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
        points = [(points[x], points[x + 1]) for x in range(0, len(points), 2)]
        ap.extend(points)
    ap.insert(0, first[0])
    return ap


def draw_ribbon(ax,
                start1, start2,
                end1, end2,
                color=_chord_pallet.blue(),
                alpha=0.6,
                radius=1.0, width=0.2, gap=0.1, **kwargs) -> PathPatch:
    corr_rad = radius - width
    start = get_ribbon_points(corr_rad - gap, width, start1, start2)
    end = get_ribbon_points(corr_rad - gap, width, end1, end2)
    verts = [start[0]]
    codes = [Path.MOVETO]
    for s in start[1:]:
        verts.append(s)
        codes.append(Path.CURVE4)
    verts.extend([(0, 0)] * 2)
    codes.extend([Path.CURVE4] * 2)
    for e in end:
        verts.append(e)
        codes.append(Path.CURVE4)
    verts.extend([(0, 0)] * 2)
    verts.append(verts[0])
    codes.extend([Path.CURVE4] * 3)
    pt = Path(verts, codes)
    pt = PathPatch(pt, facecolor=color, alpha=alpha, **kwargs)
    ax.add_patch(pt)
    return pt


def draw_chord(data,
               ax=None,
               order=None,
               offset: Union[float, List] = 5.0,
               ribbon_gap: float = 3.0,
               ribbon_kwargs: dict = None,
               arch_kwargs: dict = None,
               label_kwargs: dict = None,
               label_map: dict = None,
               use_source: bool = True,
               alpha: Union[float, dict] = 0.6,
               colors: dict = None,
               arch_height: float = 0.2,
               radius: float = 2.0,
               padding: float = 0.2,
               add_labels: bool = True,
               rotate_labels: bool = True,
               add_label_arrow: bool = False,
               color_label: bool = False,
               arrowstyle_global: str = "->",
               arrowprops_global: dict = None,
               start_angle: float = 0.0):
    if ax is None:
        _, ax = plt.subplots()  # type: plt.Axes
    amount_out = defaultdict(list)
    amount_in = defaultdict(list)
    for d in data:
        amount_out[d[0]].append(d[2])
        amount_in[d[1]].append(d[2])
    total_out = {k: sum(v) for k, v in amount_out.items()}
    total_in = {k: sum(v) for k, v in amount_in.items()}
    nodes = list(total_in.keys())
    nodes.extend(list(total_out.keys()))
    nodes = list(set(nodes))
    if order is not None:
        tmp_nodes = [x for x in nodes]
        nodes = [x for x in order if x in tmp_nodes]
        rest = [x for x in tmp_nodes if x not in order]
        nodes.extend(rest)
    total = defaultdict(int)
    for n in nodes:
        if n in total_in:
            total[n] += total_in[n]
        if n in total_out:
            total[n] += total_out[n]
    if isinstance(offset, numbers.Number):
        offset = [offset] * len(nodes)
    else:
        if len(offset) != len(nodes):
            raise ValueError(f"If offset is provided as an iterator, number "
                             f"of items should be equal to number of "
                             f"elements. Given : {len(offset)}, Required : "
                             f"{len(nodes)}.")
    angle = 360 - sum(offset)
    angle_sum = sum(total.values())
    total = {k: v * angle / angle_sum for k, v in total.items()}
    current = start_angle
    start_point = {}
    end_point = {}
    if isinstance(alpha, numbers.Number):
        alpha = {x: alpha for x in nodes}
    else:
        for n in nodes:
            if n not in alpha:
                alpha[n] = 1
    nc = _color_cycle()
    if colors is None:
        colors = {}
    if ribbon_kwargs is None:
        ribbon_kwargs = {}
    if arch_kwargs is None:
        arch_kwargs = {}
    if label_kwargs is None:
        label_kwargs = {}
    if label_map is None:
        label_map = {}
    for n in nodes:
        if n not in colors:
            colors[n] = next(nc)

    wedges = {}
    ribbons = {}
    labels = {}
    for i, n in enumerate(nodes):
        kw = {}
        if n in arch_kwargs:
            kw = arch_kwargs[n]
        start_point[n] = current
        w = draw_arch(ax, current, current + total[n],
                      radius=radius, width=arch_height,
                      color=colors[n], **kw)
        wedges[n] = w
        end_point[n] = current + total[n]
        current += total[n] + offset[i]

    used = {}
    for d in data:
        an = d[2] * angle / angle_sum
        if d[0] == d[1]:
            if d[0] in used:
                start1 = used[d[0]]
            else:
                start1 = start_point[d[0]]
            start2 = start1 + an
            end1 = start2 + ribbon_gap
            end2 = end1 + an
            used[d[0]] = end2
        else:
            if d[0] in used:
                start1 = used[d[0]]
            else:
                start1 = start_point[d[0]]
            start2 = start1 + an
            used[d[0]] = start2 + ribbon_gap
            if d[1] in used:
                end1 = used[d[1]]
            else:
                end1 = start_point[d[1]]
            end2 = end1 + an
            used[d[1]] = end2 + ribbon_gap

        key = d[1]
        if use_source:
            key = d[0]
        clr = colors[key]
        tp = alpha[key]
        kw = {"alpha": tp}
        if key in ribbon_kwargs:
            kw = {**kw, **ribbon_kwargs[key]}
        rb = draw_ribbon(ax, start1, start2, end1, end2,
                         width=arch_height,
                         radius=radius,
                         color=clr, **kw)
        r_key = f"{d[0]}-{d[1]}-{d[2]}-{len(ribbons)}"
        ribbons[r_key] = rb

    for n in nodes:
        ctr_angle = (wedges[n].theta2 - wedges[n].theta1) / 2 + wedges[
            n].theta1
        x = np.cos(np.deg2rad(ctr_angle)) * wedges[n].r
        y = np.sin(np.deg2rad(ctr_angle)) * wedges[n].r

        ha = {-1: "right", 1: "left"}[int(np.sign(x))]
        va = {-1: "top", 1: "bottom"}[int(np.sign(y))]
        rot = ctr_angle
        cs = f"angle,angleA=0,angleB={ctr_angle}"

        if ctr_angle in [0, 180]:
            va = "center"
        if 180 > rot >= 90:
            rot = -abs(180 - rot)
        elif 270 > rot >= 180:
            rot = abs(180 - rot)

        if not rotate_labels:
            rot = None
        kw = {"ha": ha, "va": va, "rotation": rot}
        if add_label_arrow:
            if rotate_labels:
                _warn("For better result, keep 'rotate_label' False when "
                      "using 'add_label_arrow'")
            kw["va"] = "center"
            kw["arrowprops"] = {"connectionstyle": cs,
                                "arrowstyle": arrowstyle_global}
            if arrowprops_global is not None:
                kw["arrowprops"] = arrowprops_global

        if color_label:
            kw["color"] = colors[n]
        if n in label_kwargs:
            kw = {**kw, **label_kwargs[n]}
        tx = n
        if n in label_map:
            tx = label_map[n]
        if add_labels and not add_label_arrow:
            a = ax.annotate(tx, xy=(x, y), **kw)
        else:
            a = ax.annotate(tx, xy=(x, y),
                            xytext=(1.3 * radius * np.sign(x), 1.4 * y), **kw)
        labels[n] = a
    padding = 1 + padding
    ax.set_xlim(-padding * radius, padding * radius)
    ax.set_ylim(-padding * radius, padding * radius)
    ax.set_aspect(1)
    ax.set_axis_off()
    return wedges, ribbons, labels, ax


def run():
    data = [
        ("a", "s", 15),
        ("w", "s", 15),
        ("t", "s", 15),
    ]
    draw_chord(data)
    plt.show()
