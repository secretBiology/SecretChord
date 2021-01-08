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

run()
from SecretChord import Arch, Ribbon

# # Creates Arch
# ar1 = Arch(1, 0, 20, height=0.2)
# ar2 = Arch(1, 50, 70, height=0.2)
# # Create Ribbon
# rb = Ribbon(ar1, ar2, start_radius=1, end_radius=1,
#             start_margin=0.1, end_margin=0.1)
# # Add Ribbons to Arch
# # Assuming data tuple is (ar1, ar2, 1)
# ar1.add_output_ribbon(rb, 1)
# ar2.add_input_ribbon(rb, 1)
# _, ax = plt.subplots()
# ax.add_patch(ar1.wedge)
# ax.add_patch(ar2.wedge)
# ax.add_patch(rb.patch)
# ax.set_aspect(1)
# plt.savefig("arch.png")
# plt.show()
