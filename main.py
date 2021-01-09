#  SecretBiology Copyright (c) 2020.
#  This library is part of SecretPlot project
#   (https://github.com/secretBiology/SecretPlots)
#
#  SecretChord : A simple library to plot the Chord Diagram
#  in native matplotlib framework
#
#


import random
import string

import matplotlib.pyplot as plt

from SecretChord import ChordDiagram


def run():
    random.seed(1000)

    def _generate_name():
        lets = [random.choice(string.ascii_letters) for _ in
                range(random.randint(2, 10))]
        return "".join(lets)

    no_arch = 40
    ribbons = 15
    arch = [_generate_name() for _ in range(no_arch)]
    data = [
        (random.choice(arch), random.choice(arch), random.randint(
            1, 30)) for _ in range(ribbons)
    ]
    cd = ChordDiagram(data)
    cd.draw(pad_factor=1.5)
    plt.tight_layout()
    plt.show()


from SecretChord import Arch, ArchLabel
import matplotlib.pyplot as plt

# Creates Arch
ar = Arch(0.7, 30, 60, height=0.1)
# Create ArchLabel
al = ArchLabel("arch_key", ar)
# here 'arch_key' is used as an placeholder.
_, ax = plt.subplots()
ax.add_patch(ar.wedge)
ax.add_artist(al.annotation)
ax.set_aspect(1)
plt.savefig("label.png")
plt.show()
