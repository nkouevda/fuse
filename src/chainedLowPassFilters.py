import random

from fuse.core import *
from fuse.primitives import *


class LowPassFilter(CustomComponent):
    def __init__(self, cutoff):
        inp, out, self.cutoff = [Node()], [Node()], cutoff
        super().__init__(inp, out, 'lpf' + str(cutoff))

    def build(self):
        self.inp >> Resistor(360) >> self.out
        Ground() >> Capacitor(1.0 / (6.28 * 360 * self.cutoff)) >> self.out


class ChainedFilters(AbstractComponent):
    def __init__(self, filter_list):
        super().__init__([Node()], [Node()])
        inp = self.inp
        for filter_component in filter_list:
            inp = inp >> filter_component
        inp >> self.out


filter_list = [LowPassFilter(x) for x in [450] * 10]
Ground() >> DCVoltageSource(1) >> ChainedFilters(filter_list) >> Resistor("1k")

spiceNetlist = CircuitEnv.compileSpiceNetlist('chainedLPFs')
print(spiceNetlist)
f = open('/Users/tomerk/Desktop/chainedLowPassFilters.cir', 'w')
f.write(spiceNetlist)
f.close()