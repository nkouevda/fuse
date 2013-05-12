# An analog -> digital converter circuit, based off:
# http://www.allaboutcircuits.com/vol_4/chpt_13/4.html
from fuse.core import *
from fuse.primitives import *

class XOrGate(CustomComponent):
    def __init__(self):
        CustomComponent.__init__(self, [Node(), Node()], [Node()], "XOR")

    def build(self):
        On = Ground() >> DCVoltageSource(5)
        Off = Ground()

        modelEither = SwitchModel(VT = 2.5) # Switch w/ voltage threshold of 2.5
        modelNeither = SwitchModel(VT = -2.5) # Switch w/ voltage threshold of -2.5
        [On] + self.inp >> Switch(modelEither) >> self.out
        [On] + self.inp[::-1] >> Switch(modelEither) >> self.out
        ([Off] + self.inp >> Switch(modelNeither)).out + self.inp[::-1] >> Switch(modelNeither) >> self.out


class GreaterThan(CustomComponent):
    def __init__(self):
        CustomComponent.__init__(self, [Node(), Node()], [Node()], "Greater")

    def build(self):
        On = Ground() >> DCVoltageSource(5)
        Off = Ground()

        model = SwitchModel()
        [On] + self.inp >> Switch(model) >> self.out
        [Off] + self.inp[::-1] >> Switch(model) >> self.out


class ThermometerEncoder(CustomComponent):
    # Create a thermometer analog -> digital encoder in the range zero_val to max_val
    def __init__(self, bits):
        inp = [Node()]
        out = Bus(bits)
        self.bits = bits
        super().__init__(inp, out, "ThermometerEncode" + str(bits))

    def build(self):
        cur_node = Ground() >> DCVoltageSource(5)
        for i in range(self.bits):
            self.inp + [cur_node] >> GreaterThan() >> self.out[self.bits - i - 1]
            cur_node = cur_node >> Resistor(1000)

        cur_node >> Ground()


class AnalogToDigital(CustomComponent):
    # Create an analog to digital encoding component
    def __init__(self, bits):
        self.bits = bits
        super().__init__([Node()], Bus(bits), "AToD" + str(bits))

    def build(self):
        # thermometer encoding logic
        thermometerComponent = ThermometerEncoder(2 ** self.bits - 1)
        self.inp >> thermometerComponent

        # Thermometer encoding -> efficient digital bit representation
        prev_node = Ground()
        mod = DiodeModel()
        for i in reversed(range(2 ** self.bits - 1)):
            xor = XOrGate()
            [prev_node, thermometerComponent.out[i]] >> xor

            # Example of making use of python functions to intelligently act
            binary_array = [int(x) for x in reversed(bin(i + 1)[2:])]
            for j, k in enumerate(binary_array):
                if k:
                    xor >> Diode(mod) >> self.out[j]

            prev_node = thermometerComponent.out[i]

desiredNum = 2
bits = 3
voltage = 5 * desiredNum / ( 2 ** bits - 1)
print("Voltage is: " + str(voltage))

Ground() >> DCVoltageSource(voltage) >> AnalogToDigital(bits) >> [Resistor("1k") >> Ground() for _ in range(bits)]

spiceNetlist = CircuitEnv.compileSpiceNetlist('AnalogToDigital')
print(spiceNetlist)
f = open('/Users/tomerk/Desktop/AnalogToDigital.cir', 'w')
f.write(spiceNetlist)
f.close()