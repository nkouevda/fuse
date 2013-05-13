# Tomer Kaftan, Nikita Kouevda, Daniel Wong
# 2013/05/12

import os
import sys
from math import pi as PI

# Add the location of the fuse source to the path before importing it
sys.path.append(
    os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from fuse.core import *
from fuse.primitives import *


class LowPassFilter(CustomComponent):
    def __init__(self, cutoff):
        self.cutoff = cutoff

        super().__init__([Node()], [Node()], 'LPF' + str(cutoff))

    def build(self):
        self.inp >> Resistor(360) >> self.out
        Ground() >> Capacitor(1.0 / (2 * PI * 360 * self.cutoff)) >> self.out


class ChainedFilters(AbstractComponent):
    def __init__(self, filter_list):
        super().__init__([Node()], [Node()])

        inp = self.inp

        for filter_component in filter_list:
            inp >>= filter_component

        inp >> self.out


def main():
    filters = ChainedFilters([LowPassFilter(x) for x in [450] * 5])
    Ground() >> ACVoltageSource(1) >> filters >> Resistor('1K') >> Ground()

    spice_netlist = CircuitEnv.compile_spice_netlist('chainedLPFs')
    spice_netlist = (
        spice_netlist[:-4] + '.AC DEC 10 10 100k\n'
        + '.plot AC Vdb(1) Vdb(2) Vdb(3) Vdb(4) Vdb(5) Vdb(6)\n' + spice_netlist[-4:])

    print(spice_netlist)

    with open('chainedLowPassFilters.cir', 'w') as out_file:
        out_file.write(spice_netlist)


if __name__ == '__main__':
    main()
