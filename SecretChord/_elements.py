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
    """
    Generic Class to generate common methods for all the elements

    .. danger::
       DO NOT use it in your workflow unless you are constructing your own
       custom class

    """

    def __init__(self):
        self._center = None
        self._is_visible = True
        self.kwargs = {}

    @property
    def center(self) -> tuple:
        """
        Center around which :class:`~SecretChord.Arch` is created or
        :class:`~SecretChord.Ribbon` is bent. This will be ignored for
        :class:`~SecretChord.ArchLabel`  as it will use corresponding
        :class:`~SecretChord.Arch`'s center internally.

        Default is (0,0).

        :return: tuple (x,y) representing x and y coordinates of the center
        """
        if self._center is None:
            self._center = (0, 0)
        return self._center

    @center.setter
    def center(self, value: tuple):
        self._center = value

    def hide(self):
        """
        Hide element from the graph.
        """
        self._is_visible = False

    def show(self):
        """
        Show element in the graph
        """
        self._is_visible = True

    @property
    def is_visible(self) -> bool:
        """ Is current object visible on the graph?
        :return: True if yes, otherwise False
        """
        return self._is_visible

    def update(self, **kwargs):
        """
        Update the named parameter which will be passed to corresponding
        matplotlib object.

        :param kwargs: named parameters
        """
        self.kwargs = {**self.kwargs, **kwargs}


class Arch(CommonMethods):
    """
    Arch resides on the periphery of the ChordDiagram and represents the
    amount of ribbons originating or ending up on respective variable.
    Visually it is the thick portion at the end of ribbon. Proportion of
    arch is calculated automatically based on amount coming in / going out,
    total angle available and gap between two arch.

    :class:`~SecretChord.Arch` inherits :class:`~SecretChord.CommonMethods`
    and all of its methods.

    In some R packages like 'circlize' arch are the part of 'sectors'
    on given 'tracks'. Do not confuse the terminology.

    Internally, it creates 'matplotlib.patches.Wedge' object and returns it
    back for plotting. Simple arch can be made easily like following,

    .. code-block:: python

        from SecretChord import Arch
        import matplotlib.pyplot as plt


        ar = Arch(1, 30, 60, height=0.2)
        _, ax = plt.subplots()
        ax.add_patch(ar.wedge)
        ax.set_aspect(1)
        plt.show()

    .. image:: images/arch.png
        :width: 400
        :align: center
        :alt: Alternative text

    Various parameters which you can freely adjust are shown in above
    figure. All the angles are calculated from positive x-axis. In addition
    to these, you can also adjust Wedge parameters as per matplotlib's
    documentation.

    In addition to all the options available here, you can use
    `Arch.update()` method to add any additional named parameters
    which will be passed to matplotlib.patches.Wedge

    """

    def __init__(self, radius: float,
                 start_angle: float, end_angle: float, *,
                 height: float,
                 **kwargs):
        """
        :param radius: radius from the center till outer edge of the arch
        :param start_angle: start angle along positive x-axis
        :param end_angle: end angle along positive x-axis
        :param height: height of the arch (or width of the wedge)
        :param kwargs: other named parameters which will be passed to Wedge
        """
        super().__init__()
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.kwargs = kwargs
        self.height = height

        self._wedge = None
        self._destinations = OrderedDict()
        self._origins = OrderedDict()

    def __repr__(self):
        return f"Arch({self.start_angle},{self.end_angle})"

    @property
    def wedge(self) -> Wedge:
        """
        Returns matplotlib.patches.Wedge which can be added to matplotlib.Axes
        """
        if self._wedge is None:
            self._wedge = Wedge(center=self.center,
                                r=self.radius,
                                theta1=self.start_angle, theta2=self.end_angle,
                                width=self.height,
                                **self.kwargs)
        return self._wedge

    @property
    def destinations(self) -> OrderedDict:
        return self._destinations

    @property
    def angle(self) -> float:
        """
        Total angle covered by the arch
        """
        return self.end_angle - self.start_angle

    @property
    def origins(self) -> OrderedDict:
        return self._origins

    def add_as_destination(self, ribbon, amount):
        """
        Add :class:`~SecretChord.Ribbon` whose destination is current
        arch i.e. where arch key is represented at the second position in
        the data tuple.

        :param ribbon: :class:`~SecretChord.Ribbon` object
        :param amount: amount covered by the ribbon object
        """
        self._destinations[ribbon] = amount

    def add_as_origin(self, ribbon, amount):
        """
        Add :class:`~SecretChord.Ribbon` whose origin is current arch.
        i.e. where arch key is represented at the first position in the
        data tuple.

        :param ribbon: :class:`~SecretChord.Ribbon` object
        :param amount: amount covered by the ribbon object
        """
        self._origins[ribbon] = amount

    def get_order(self) -> tuple:
        """
        Get ordered list of origin and destination ribbons
        """
        nodes_val = list(self.origins.values())
        nodes_val.extend(list(self.destinations.values()))
        total = sum(nodes_val)
        nodes_val = [x * self.angle / total for x in nodes_val]
        return nodes_val[:len(self.origins)], nodes_val[
                                              len(self.origins):]

    def get_angle(self, node, is_origin):
        """
        Get start_angle for the given ribbon object near current arch

        :param node: :class:`~SecretChord.Ribbon` object
        :param is_origin: If ribbon is originating from current arch
        :return: start_angle for given :class:`~SecretChord.Ribbon` on
           current :class:`~SecretChord.Arch`
        """
        val_origin, val_dest = self.get_order()
        current = self.start_angle
        val = val_dest
        val_ref = self.destinations
        if is_origin:
            val_dest.append(0)  # To avoid empty sum
            current += sum(val_dest)
            val = val_origin
            val_ref = self.origins

        for v in val_ref:
            if v == node:
                return current, current + val[0]
            else:
                current += val[0]
                val.pop(0)

        raise AttributeError("Wrong Ribbon direction or Wrong Arch")


class Ribbon(CommonMethods):
    """
    In this library, Ribbons are the links of chord diagrams. They
    originates from one arch and end at their destination arch. However,
    current library provides you full flexibility. You can have ribbons
    anywhere :)

    :class:`~SecretChord.Ribbon` inherits :class:`~SecretChord.CommonMethods`
    and all of its methods.

    In some R packages like 'circlize' ribbons are called 'links'.

    Internally, it creates 'matplotlib.patches.PathPatch' object and returns it
    back for plotting. Creating ribbon from scratch needs little bit work.
    However, you will rarely need to create it from the scratch.

    .. code-block:: python

        from SecretChord import Arch, Ribbon
        import matplotlib.pyplot as plt

        # Creates Arch
        ar1 = Arch(1, 10, 20, height=0.1)
        ar2 = Arch(1, 60, 70, height=0.1)
        # Create Ribbon
        rb = Ribbon(ar1, ar2, origin_radius=1, destination_radius=1,
                    origin_margin=0.1, destination_margin=0.1)
        # Add Ribbons to Arch
        # Assuming data tuple is (ar1, ar2, 1)
        ar1.add_as_origin(rb, 1)
        ar2.add_as_destination(rb, 1)
        _, ax = plt.subplots()
        ax.add_patch(ar1.wedge)
        ax.add_patch(ar2.wedge)
        ax.add_patch(rb.patch)
        ax.set_aspect(1)
        plt.show()


    Above code will generate two arch. Where origin arch is starting at 10
    degree and ending at 20 degree while destination arch starts at 60 and
    ends at 70. Both have radius of 1. When we do not provide radius,
    it uses default (0,0). Then we create the Ribbon by providing all the
    details and origin-destination arch objects.

    One important step where you will get your 99% of "Wrong Ribbon
    direction or Wrong Arch" Attribute errors is adding ribbon back to arch.
    This looks counter-intuitive but for current designed, we need to do it.
    This can be achieved by using 'Arch.add_as_destination()' and
    'Arch.add_as_origin()' functions as shown in above code-block. It will
    then generate the ribbon as shown in following figure.

    .. image:: images/ribbon.png
        :width: 400
        :align: center
        :alt: Alternative text

    Various parameters which you can freely adjust are shown in above
    figure. In addition to these, you can also adjust PathPatch parameters as
    per matplotlib's documentation.

    .. warning::
      `origin_radius` and `destination_radius` are the distance
      from the center of corresponding `origin_arch` and `destination_arch`
      and NOT from `bending_center`. In above image, we have not specified any
      center and hence all the centers are (0,0)


    bending_radius defines the 3rd point of matplotlib's middle point
    of Bézier curve. Internally it uses 'CURVE4'.

    In addition to all the options available here, you can use
    `Ribbon.update()` method to add any additional named parameters
    which will be passed to matplotlib.patches.PathPatch
    """

    def __init__(self, origin_arch: Arch, destination_arch: Arch, *,
                 origin_radius: float, destination_radius: float,
                 origin_margin: float, destination_margin: float,
                 **kwargs):
        """
        :param origin_arch: Arch from where current ribbon is originating
        :param destination_arch: Arch where current ribbon is ending
        :param origin_radius: length of ribbon from center of origin_arch
        :param destination_radius: length of ribbon from center of
            destination_arch
        :param origin_margin: margin to be left near origin_arch
        :param destination_margin: margin to be left near destination_arch
        :param kwargs: named parameters which will be passed to PathPatch
            object during plotting
        """
        super().__init__()
        self.origin_arch = origin_arch
        self.destination_arch = destination_arch
        self.origin_margin = origin_margin
        self.destination_margin = destination_margin
        self._origin_radius = origin_radius
        self._destination_radius = destination_radius
        self.kwargs = kwargs
        self._patch = None
        self.bend_center = None

    def __repr__(self):
        return f"Ribbon({self.origin_arch},{self.destination_arch})"

    @property
    def origin_radius(self) -> float:
        """
        length of ribbon from center of origin_arch. If not given, radius
        from the origin_arch will be used.
        """
        if self._origin_radius is None:
            return self.origin_arch.radius
        return self._origin_radius

    @origin_radius.setter
    def origin_radius(self, value: float):
        self._origin_radius = value

    @property
    def destination_radius(self) -> float:
        """
        length of ribbon from center of destination_arch. If not given,
        radius from the destination_arch will be used
        """
        if self._destination_radius is None:
            return self.destination_arch.radius
        return self._destination_radius

    @destination_radius.setter
    def destination_radius(self, value: float):
        self._destination_radius = value

    @staticmethod
    def get_points(start, end, radius, margin, arch: Arch):
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
    def patch(self) -> PathPatch:
        """
        PatchPatch object which can be directed added to matplotlib axes.
        """
        if self._patch is None:
            sp1, sp2 = self.origin_arch.get_angle(self, True)
            ep1, ep2 = self.destination_arch.get_angle(self, False)

            sp = self.get_points(sp1, sp2, self.origin_radius,
                                 self.origin_margin, self.origin_arch)

            ep = self.get_points(ep1, ep2, self.destination_radius,
                                 self.destination_margin,
                                 self.destination_arch)

            pt = self.get_path(sp, ep)
            self._patch = PathPatch(pt, **self.kwargs)
        return self._patch


class ArchLabel(CommonMethods):
    """
    Arch Labels are the labels which will be placed next to corresponding arch.

    :class:`~SecretChord.ArchLabel` inherits
    :class:`~SecretChord.CommonMethods`
    and all of its methods. However, the radius field will be ignored.
    Instead the radius from the corresponding arch will be used in all of
    the calculations

    Following parameters can be adjusted directly,

     * rotate: If True, labels will be rotated along the radius (default: True)
     * add_arrow: If True, adds `arrowprops` to the annotation which will \
     create the labels away from the chord diagram and \
     corresponding arrows will be added to point the arch
     * arrowstyle: arrow style of annotations. Only applies when add_arrow\
     is True. (default: '->')
     * arrow_label_x_factor: this factor will be multiplied to x value \
     while placing the label with arrow. (default: 1.2)
     * arrow_label_y_factor: this factor will be multiplied to y value \
     while placing the label with arrow. (default: 1.2)
     * rotation_mode: for text annotation (default: anchor)
     * wrap_words: Numbers of words after which label should wrap. Number \
     of words are calculated by splitting text with space. (default: Infinite)
     * label_gap: Gap between arch and label


    In addition to all the options available here, you can use
    `ArchLabel.update()` method to add any additional named parameters
    which will be passed to matplotlib.text.Annotation.



    """

    def __init__(self, arch_key: str, arch: Arch):
        """
        :param arch_key: data variable associated with arch
        :param arch: :class:`~SecretChord.Arch` object
        """
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
        """
        Distance of label from the arch center.
        (default : arch.radius + label_gap)
        """
        if self._radius is None:
            return self.arch.radius + self.label_gap
        return self._radius

    @radius.setter
    def radius(self, value: float):
        self._radius = value

    @property
    def angle(self):
        """
        Angle of rotation of text
        """
        if self._angle is None:
            return self.arch.start_angle + (self.arch.end_angle -
                                            self.arch.start_angle) / 2
        return self._angle

    @angle.setter
    def angle(self, value: float):
        self._angle = value

    @property
    def text(self):
        """
        Text to display.

        If not provided, arch key from the data tuple will
        be used. For example, if your data is ("apple", "orange", 2),
        the two arches will have key (as well as text) as "apple" and "orange".
        """
        if self._text is None:
            return str(self.arch_key)
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
        """
        Reruns the matplotlib.text.Annotation associated with this ArchLabel.
        """
        if self._annotation is None:
            if self.add_arrow:
                self._with_arrow()
            else:
                self._regular()
        return self._annotation
