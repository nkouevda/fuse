# Tomer Kaftan, Nikita Kouevda, Daniel Wong
# 2013/05/15

"""An analog to digital converter circuit.

Based on <http://www.allaboutcircuits.com/vol_4/chpt_13/4.html>.
"""

import os
import sys

# Add the location of the fuse source to the path before importing it
sys.path.append(
    os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from fuse import *


class XOrGate(CustomComponent):
    def __init__(self):
        CustomComponent.__init__(self, [Node(), Node()], [Node()], 'XOR')

    def build(self):
        On = Ground() >> DCVoltageSource(5)
        Off = Ground()

        # Switches with voltage thresholds of 2.5 and -2.5
        model_either = SwitchModel(VT=2.5)
        model_neither = SwitchModel(VT=-2.5)

        # XOR logic
        [On] + self.inp >> Switch(model_either) >> self.out
        [On] + self.inp[::-1] >> Switch(model_either) >> self.out
        (([Off] + self.inp >> Switch(model_neither)).out + self.inp[::-1]
         >> Switch(model_neither) >> self.out)


class GreaterThan(CustomComponent):
    def __init__(self):
        CustomComponent.__init__(
            self, [Node(), Node()], [Node()], 'GT')

    def build(self):
        model = SwitchModel()

        ([Ground() >> DCVoltageSource(5)] + self.inp >> Switch(model)
         >> self.out)

        [Ground()] + self.inp[::-1] >> Switch(model) >> self.out


class ThermometerEncoder(CustomComponent):
    def __init__(self, bits):
        inp, out, self.bits = [Node()], Bus(bits), bits
        super().__init__(inp, out, 'TE' + str(bits))

    def build(self):
        current_node = Ground() >> DCVoltageSource(5)

        for i in range(self.bits):
            (self.inp + [current_node] >> GreaterThan()
             >> self.out[self.bits - i - 1])

            current_node >>= Resistor(1000)

        current_node >> Ground()


class AnalogToDigital(CustomComponent):
    # Create an analog to digital encoding component
    def __init__(self, bits):
        self.bits = bits
        super().__init__([Node()], Bus(bits), 'ATOD' + str(bits))

    def build(self):
        # Thermometer encoding logic
        thermometerComponent = ThermometerEncoder(2 ** self.bits - 1)
        self.inp >> thermometerComponent

        # Thermometer encoding to efficient digital bit representation
        prev_node = Ground()
        mod = DiodeModel()

        for i in reversed(range(2 ** self.bits - 1)):
            xor = XOrGate()
            [prev_node, thermometerComponent.out[i]] >> xor

            binary_array = [int(x) for x in reversed(bin(i + 1)[2:])]

            for j, k in enumerate(binary_array):
                if k:
                    xor >> Diode(mod) >> self.out[j]

            prev_node = thermometerComponent.out[i]


def main():
    desired_num = 2
    bits = 3
    voltage = 5 * desired_num / (2 ** bits - 1)

    # Indicate the voltage being used
    print('Voltage is: ' + str(voltage))

    (Ground() >> DCVoltageSource(voltage) >> AnalogToDigital(bits)
     >> [Resistor('1K') >> Ground() for _ in range(bits)])

    # Generate the netlist
    spice_netlist = CircuitEnv.compile_spice_netlist('AnalogToDigital')

    print(spice_netlist)

    with open('analog_to_digital.cir', 'w') as out_file:
        out_file.write(spice_netlist)


if __name__ == '__main__':
    main()
