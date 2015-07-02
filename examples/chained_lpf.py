#!/usr/bin/env python3

import os
import sys
from math import pi as PI

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from fuse import *


class LowPassFilter(CustomComponent):
    def __init__(self, cutoff):
        self.cutoff = cutoff

        super().__init__([Node()], [Node()], 'LPF' + str(cutoff))

    def build(self):
        self.inp >> Resistor(360) >> self.out

        # Use the given cutoff
        Ground() >> Capacitor(1.0 / (2 * PI * 360 * self.cutoff)) >> self.out


class ChainedFilters(AbstractComponent):
    def __init__(self, filter_list):
        super().__init__([Node()], [Node()])

        # Use the input from super().__init__
        inp = self.inp

        # Connect each of the given filters in series
        for filter_component in filter_list:
            inp >>= filter_component

        inp >> self.out


def main():
    # Use 5 chained filters
    filters = ChainedFilters([LowPassFilter(x) for x in [450] * 5])

    # Connect them to an AC source and a resistor
    Ground() >> ACVoltageSource(1) >> filters >> Resistor('1K') >> Ground()

    # Generate the netlist
    spice_netlist = CircuitEnv.compile_spice_netlist('ChainedLPF')

    # Add AC analysis
    spice_netlist = (
        spice_netlist[:-4] + '.AC DEC 10 10 100k\n'
        + '.plot AC Vdb(1) Vdb(2) Vdb(3) Vdb(4) Vdb(5) Vdb(6)\n'
        + spice_netlist[-4:])

    print(spice_netlist)

    with open('chained_lpf.cir', 'w') as out_file:
        out_file.write(spice_netlist)


if __name__ == '__main__':
    main()
