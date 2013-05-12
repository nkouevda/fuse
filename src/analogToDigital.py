# An analog -> digital converter circuit, based off:
# http://www.allaboutcircuits.com/vol_4/chpt_13/4.html
from fuse.core import *
from fuse.primitives import *

On = Ground() >> DCVoltageSource(1)
Off = Ground()

class XOrGate(CustomComponent):
    pass

class GreaterThan(CustomComponent):
    pass

class ThermometerEncoder(CustomComponent):
    # Create a thermometer analog -> digital encoder in the range zero_val to max_val

    def __init__(self, bits):
        inp = [Node()]
        out = Bus(bits)
        self.bits = bits
        super().__init__(inp, out, "ThermometerEncode" + str(bits))

    def build(self):
        resistance = 1000

        cur_node = On
        for i in range(self.bits):
            comparator = OpAmp()
            comparator.connect(Bundle([self.input, cur_node, high, low]))
            self.output[i].connect(comparator)

            resistor = Resistor(resistance)
            resistor.connect(cur_node)
            cur_node = resistor

        cur_node >> Ground()


class AnalogToDigital(Component):
    # Create an analog to digital encoding component
    def __init__(self, bits, max_voltage):
        self.input = Node()
        self.output = Bundle([Node() for x in range(bits)])

        # thermometer encoding logic
        thermometerComponent = ThermometerEncoder(2 ** bits - 1, max_voltage)
        thermometerComponent.connect(self.input)

        # Thermometer encoding -> efficient digital bit representation
        prev_node = ground
        for i in reversed(range(2 ** bits - 1)):
            xor = XOrGate()
            xor.connect(Bundle(prev_node, thermometerComponent.output[i]))

            # Example of making use of python functions to intelligently act
            binary_array = [int(x) for x in reversed(bin(i+1)[2:])]
            for j, k in enumerate(binary_array):
                if k:
                    self.output[j].connect(Diode(xor))

            prev_node = thermometerComponent.output[i]

        #Make sure that we set stuff relative to ground
        for i in range(bits):
            resistor = Resistor(2000)
            resistor.connect(self.output[i])
            ground.connect(resistor)

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