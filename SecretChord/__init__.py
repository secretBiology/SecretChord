#  SecretBiology Copyright (c) 2020
#
#  This library is part of SecretPlot project
#  (https://github.com/secretBiology/SecretPlots)
#
#  SecretChord : A simple library to plot the Chord Diagram
#  in native matplotlib framework

import matplotlib.pyplot as plt
from SecretColors import Palette

from SecretChord._elements import CommonMethods, Arch, ArchLabel, Ribbon
from SecretChord._base import Track


class ChordDiagram:
    """
    :class:`~SecretChord.ChordDiagram` is the main class for generating Chord
    Diagrams. It acts as a wrapper around all other components of your graph.



    Creating beautiful chord diagrams is as easy as following,

    .. code-block:: python

      from SecretChord import ChordDiagram
      data = [("a", "b", 2), ("a", "c", 5), ("c", "d", 4)]
      ChordDiagram(data).show()


    You can control every aspect of your graph with this library making it
    easier to visualize complex graphs with ease. For better control over
    your graph, we recommend using it as an object.

    .. code-block:: python

      from SecretChord import ChordDiagram
      import matplotlib.pyplot as plt

      data = [("apple", "banana", 20), ("apple", "orange", 10)]
      _, ax = plt.subplots()
      cd = ChordDiagram(data)
      cd.track.radius = 1.3
      cd.highlight_arch("apple")
      cd.draw(ax)
      plt.show()

    """

    def __init__(self, data):
        """
        :class:`~SecretChord.ChordDiagram` should be initialized with your
        data. Your data should be in specific 'flow' format. This is
        different from many other chord diagram generator which accepts the
        data in the form of matrix. One advantage of representing data in
        this way is that it is very intuitive. Additionally, it allows
        duplicate data or self loops very efficiently. Your data should be
        list of tuples with following format.

        .. code-block:: python

            [ (start1, end1, amount1), (start2, end2, amount2) ... ]

        Where first two elements will be the variable between which you are
        drawing the relationship. Third element in the tuple is amount.
        Library will automatically convert your amounts into the appropriate
        percentage of chord.

        It accepts variables in any object type. However, we recommend
        using `str` to avoid confusion during debugging and to avoid unwanted
        bugs.

        .. danger::
            Keep the amount units same. If you have data in multiple units,
            convert them into one single unit and then add it to the
            ChordDiagram.

        :param data: your data with flow format (see description)
        """
        self.data = data
        self._track = None

    @property
    def track(self) -> Track:
        """
        Returns underlying :class:`~SecretChord.Track` object which you can
        further use for customizations.

        >>> cd = ChordDiagram(data)
        >>> cd.track.radius = 1.4

        :return: :class:`~SecretChord.Track` object
        """
        if self._track is None:
            trc = Track()
            trc.add_data(self.data)
            self._track = trc
        return self._track

    def arch(self, key) -> Arch:
        """
        Returns specific :class:`~SecretChord.Arch` associated with given
        variable key. Internally we store all the :class:`~SecretChord.Arch`
        of each track in dictionary where key is the variable  of the given
        arch.

        For example, if your data is following,

        >>> data = [("a", "b", 33), ("b", "c", 3)]

        Arch associated with **a** can be retrieved as following

        >>> ChordDiagram(data).arch("a")

        :param key: variable provided in data tuples
        :return: :class:`~SecretChord.Arch` object associated with given key
        """
        return self.track.get_arch(key)

    def ribbon(self, data_entry: tuple, index: int) -> Ribbon:
        """
        Returns specific :class:`~SecretChord.Ribbon` associated with given
        data tuple and its index. Internally we store
        :class:`~SecretChord.Ribbon` in the dictionary where keys are
        **data_entry-index** of each ribbon. Here, we use index because this
        library allows duplicate data entries. Hence, to differentiate
        between these, we use index.

        For example, if your data is following,

        >>> data = [("a", "b", 33), ("b", "c", 3)]

        Ribbon associated with first data entry `("a","b",33)` can be
        retireve as following

        >>> ChordDiagram(data).ribbon(("a","b", 33),0)
        >>> ChordDiagram(data).ribbon(data[0],0) # Or simply

        :param data_entry: Data tuple as provided in the data
        :param index: Index of the tuple in your data
        :return: :class:`~SecretChord.Ribbon` object
        """
        return self.track.get_ribbon(data_entry, index)

    def arch_label(self, key) -> ArchLabel:
        """
        Returns specific :class:`~SecretChord.ArchLabel` object associated
        with the given key. Internally, we store all
        :class:`~SecretChord.ArchLabel` objects in the dictionary where key
        is the :class:`~SecretChord.Arch` key or respective label.

        For example, if your data is following,

        >>> data = [("a", "b", 33), ("b", "c", 3)]

        ArchLabel associated with **b** can be retrieved as following

        >>> ChordDiagram(data).arch_label("b")


        :param key: key associated with corresponding
           :class:`~SecretChord.Arch` object
        :return: :class:`~SecretChord.ArchLabel` object
        """
        return self.track.get_arch_label(key)

    def update_arch(self, **kwargs):
        """
        Updates given properties of **ALL** arch of the graph. These
        parameters will be passed to `matplotlib.patches.Wedge` object
        generated by :class:`~SecretChord.Arch`. Take a look at `Wedge
        <https://matplotlib.org/3.3.3/api/_as_gen/matplotlib.patches.Wedge.html>`_
        documentation to get more information about which parameters can be
        passed.

        :param kwargs: named Parameters
        """
        self.track.update_arch(**kwargs)

    def update_ribbons(self, **kwargs):
        """
        Updates given properties of **ALL** ribbons of the graph. These
        parameters will be passed to `matplotlib.patches.PathPatch` object
        generated by :class:`~SecretChord.Ribbon`. Take a look at `PathPatch
        <https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.patches.PathPatch.html>`_
        documentation to get more information about which parameters can be
        passed.

        :param kwargs: named Parameters
        """
        self.track.update_ribbons(**kwargs)

    def update_arch_labels(self, **kwargs):
        """
        Updates given properties of **ALL** arch labels of the graph. These
        parameters will be passed to `matplotlib.text.Annotation` object
        generated by :class:`~SecretChord.ArchLabel`. Take a look at
        `Annotation
        <https://matplotlib.org/3.1.1/api/text_api.html#matplotlib.text.Annotation>`_
        documentation to get more information about which parameters can be
        passed.

        :param kwargs: named Parameters
        """
        self.track.update_arch_labels(**kwargs)

    def fade_all(self, background_alpha: float = 0.3):
        """
        Fades all :class:`~SecretChord.Arch`,
        :class:`~SecretChord.ArchLabel` and :class:`~SecretChord.Ribbon`
        from the graph

        :param background_alpha: amount of fading [default: 0.3]
        """
        self.update_arch(alpha=background_alpha)
        self.update_ribbons(alpha=background_alpha, ec="None")
        self.update_arch_labels(alpha=background_alpha)

    def highlight_arch(self, key, fade: bool = True, background_alpha=0.3):
        """
        Highlights given :class:`~SecretChord.Arch` and
        :class:`~SecretChord.ArchLabel` associated with it by changing its
        transparency to 1. while fading others (if `fade` is True)

        :param key: :class:`~SecretChord.Arch` key
        :param fade: if True, will fade all other components
        :param background_alpha: amount of fading [default: 0.3]
        """
        if fade:
            self.fade_all(background_alpha)
        self.arch(key).update(alpha=1)
        self.arch_label(key).update(alpha=1)

    def highlight_ribbon(self, data_entry: tuple, index: int,
                         fade: bool = True,
                         background_alpha=0.3):
        """
        Highlights given :class:`~SecretChord.Ribbon` and
        :class:`~SecretChord.ArchLabel` associated with it by changing its
        transparency to 1. while fading others (if `fade` is True)

        :param data_entry: data entry for given ribbon
        :param index: index of data entry in the data
        :param fade: if True, will fade all other components
        :param background_alpha: amount of fading [default: 0.3]
        """
        if fade:
            self.fade_all(background_alpha)
        self.ribbon(data_entry, index).update(alpha=1)
        self.arch_label(data_entry[0]).update(alpha=1)
        self.arch_label(data_entry[1]).update(alpha=1)

    def highlight_flow(self, data_entry: tuple, index: int,
                       fade: bool = True,
                       background_alpha: float = 0.3):
        """
        Highlights given :class:`~SecretChord.Ribbon`,
        :class:`~SecretChord.Arch` and
        :class:`~SecretChord.ArchLabel` associated with by changing its
        transparency to 1. while fading others (if `fade` is True)

        :param data_entry: data entry for given ribbon
        :param index: index of data entry in the data
        :param fade: if True, will fade all other components
        :param background_alpha: amount of fading [default: 0.3]
        """
        if fade:
            self.fade_all(background_alpha)
        self.ribbon(data_entry, index).update(alpha=1)
        self.arch(data_entry[0]).update(alpha=1)
        self.arch(data_entry[1]).update(alpha=1)
        self.arch_label(data_entry[0]).update(alpha=1)
        self.arch_label(data_entry[1]).update(alpha=1)

    def highlight_elements(self, key, fade: bool = True, background_alpha=0.3):
        """
        Highlights all ribbons, arch labels and arch associated with given key.

        :param key: variable used in the data
        :param fade: if True, will fade all other components
        :param background_alpha: amount of fading [default: 0.3]
        """
        if fade:
            self.fade_all(background_alpha)
        self.arch(key).update(alpha=1)
        for i, d in enumerate(self.data):
            if d[0] == key or d[1] == key:
                self.ribbon(d, i).update(alpha=1)
                self.arch_label(d[0]).update(alpha=1)
                self.arch_label(d[1]).update(alpha=1)

    def draw(self, ax: plt.Axes = None, pad_factor=1.2):
        """
        Draws everything on given axes.

        :param ax: matplotlib.Axes
        :param pad_factor: Margin surrounding the graph. This factor will
           be multiplied to the radius of the chord diagram
        :return: matplotlib.Axes on which graph is drawn
        """
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

    def show(self, ax: plt.Axes = None, **kwargs):
        """
        Shows the graph without saving

        :param ax: matplotlib.Axes
        :param kwargs: named parameters
        """
        self.draw(ax)
        plt.show(**kwargs)


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
