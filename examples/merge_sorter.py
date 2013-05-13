# Tomer Kaftan, Nikita Kouevda, Daniel Wong
# 2013/05/12

import os
import random
import sys

# Add the location of the fuse source to the path before importing it
sys.path.append(
    os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from fuse.core import *
from fuse.primitives import *


class Comparator(CustomComponent):
    def __init__(self):
        super().__init__(Bus(2), Bus(2), 'CMP')

    def build(self):
        switchModel = SwitchModel()

        [self.inp[0]] + self.inp >> Switch(switchModel) >> self.out[0]
        [self.inp[0]] + self.inp[::-1] >> Switch(switchModel) >> self.out[1]
        [self.inp[1]] + self.inp >> Switch(switchModel) >> self.out[1]
        [self.inp[1]] + self.inp[::-1] >> Switch(switchModel) >> self.out[0]


class OddEvenMerger(CustomComponent):
    def __init__(self, n, explode=False):
        self.n = n
        super().__init__(
            [Bus(n), Bus(n)], Bus(2 * n), 'MERGE' + str(n * 2),
            explode=explode)

    def build(self):
        n, inp, out = self.n, self.inp, self.out

        if n == 1:
            inp >> Comparator() >> out
        else:
            odd = inp[0][::2], inp[1][::2]
            odd_merger = odd >> OddEvenMerger(n // 2, explode=True)
            odd_merger.out[0] >> out[0]

            even = inp[0][1::2], inp[1][1::2]
            even_merger = even >> OddEvenMerger(n // 2, explode=True)
            even_merger.out[n - 1] >> out[2 * n - 1]

            for i in range(n - 1):
                ([odd_merger.out[i + 1], even_merger.out[i]] >> Comparator()
                 >> [out[2 * i + 1], out[2 * i + 2]])


class OddEvenMergeSort(CustomComponent):
    def __init__(self, n, explode=False):
        self.n = n
        super().__init__(Bus(n), Bus(n), 'SORT' + str(n), explode=explode)

    def build(self):
        n, inp, out = self.n, self.inp, self.out

        if n == 1:
            inp >> out
        else:
            a = inp[:n // 2] >> OddEvenMergeSort(n // 2, explode=True)
            b = inp[n // 2:] >> OddEvenMergeSort(n // 2, explode=True)

            [a, b] >> OddEvenMerger(n // 2) >> out


def main():
    num = 16

    inp = [Ground() >> DCVoltageSource(random.random()) for _ in range(num)]
    out = [Resistor(1000) >> Ground() for i in range(num)]
    inp >> OddEvenMergeSort(num) >> out

    spice_netlist = CircuitEnv.compile_spice_netlist('MergeSorter')

    print(spice_netlist)

    with open('sorter.cir', 'w') as out_file:
        out_file.write(spice_netlist)


if __name__ == '__main__':
    main()
