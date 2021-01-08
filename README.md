### SecretChord

[![PyPI version](https://badge.fury.io/py/SecretChord.svg)](https://badge.fury.io/py/SecretChord)
![GitHub](https://img.shields.io/github/license/secretBiology/SecretChord)

Generate robust and beautiful Chord Diagrams with pure matplotlib.

`matplotlib` wrapper for [Chord](https://en.wikipedia.org/wiki/Chord_diagram)
Diagrams. This is a part
of [SecretPlot](https://github.com/secretBiology/SecretPlots)
project.

Beta version is available for testing. Install by following command,

    pip install SecretChord


Creating chord diagrams is as simple as following,

    from SecretChord import ChordDiagram
    data = [("a", "b", 2), ("a", "c", 5), ("c", "d", 4)]
    ChordDiagram(data).show()

Please share your feedback :)