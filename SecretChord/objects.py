#  SecretBiology Copyright (c) 2020.
#  This library is part of SecretPlot project
#  (https://github.com/secretBiology/SecretPlots)
#
#  SecretChord : A simple library to plot the Chord Diagram
#  in native matplotlib framework
#
#
import matplotlib.pyplot as plt
import numpy as np
from SecretColors import Palette
from matplotlib.patches import (Wedge, Path,
                                PathPatch)

_chord_pallet = Palette()

RIBBON_CODE = [
    Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
    Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
    Path.CLOSEPOLY,
]


def curve_point(r, theta):
    return [r * np.cos(theta), r * np.sin(theta)]


def simple_arch(ax, start, end, width=0.2,
                radius=1.0,
                offset=0,
                color=_chord_pallet.blue(), **kwargs):
    w = Wedge(center=(0, 0),
              r=radius,
              theta1=offset + start,
              theta2=offset + end,
              width=width,
              facecolor=color, **kwargs)
    ax.add_patch(w)


def get_ribbon_start(radius, width, start, end):
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


def simple_ribbon(ax,
                  start1, start2,
                  end1, end2,
                  radius=1, width=0.2, gap=0.1):
    corr_rad = radius - width
    start = get_ribbon_start(corr_rad - gap, width, start1, start2)
    end = get_ribbon_start(corr_rad - gap, width, end1, end2)
    verts = [start[0]]
    codes = [Path.MOVETO]
    for s in start[1:]:
        verts.append(s)
        codes.append(Path.CURVE4)
    verts.append(end[0])
    codes.append(Path.LINETO)
    for e in end[1:]:
        verts.append(e)
        codes.append(Path.CURVE4)

    pt = Path(verts, codes)
    ax.add_patch(PathPatch(pt))


def run():
    _, ax = plt.subplots()  # type: plt.Axes
    s1, s2 = 0, 30
    e1, e2 = 140, 270
    simple_arch(ax, s1, s2)
    simple_arch(ax, e1, e2)
    simple_ribbon(ax, s1, s2, e1, e2 - 30)
    plt.xlim(-2, 2)
    plt.ylim(-2, 2)
    ax.set_aspect(1)
    plt.axhline(0)
    plt.axvline(0)
    plt.show()
