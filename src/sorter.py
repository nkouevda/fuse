import random

from fuse.core import *
from fuse.primitives import *

class Comparator(CustomComponent):
    def __init__(self):
        inp, out = [Node(), Node()], [Node(), Node()]
        super().__init__(inp, out, 'comparator')

    def build(self):
        switchModel = SwitchModel()
        [self.inp[0]] + self.inp >> Switch(switchModel) >> self.out[0]
        [self.inp[0]] + self.inp[::-1] >> Switch(switchModel) >> self.out[1]
        [self.inp[1]] + self.inp >> Switch(switchModel) >> self.out[1]
        [self.inp[1]] + self.inp[::-1] >> Switch(switchModel) >> self.out[0]


class OddEvenMerger(CustomComponent):
    def __init__(self, n, explode=False):
        self.n = n
        inp = [[Node() for _ in range(n)], [Node() for _ in range(n)]]
        out = [Node() for _ in range(2 * n)]
        componentName = 'merge' + str(n * 2)
        super().__init__(inp, out, componentName, explode=explode)

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
                ([odd_merger.out[i + 1], even_merger.out[i]]
                 >> Comparator() >> [out[2 * i + 1], out[2 * i + 2]])


class OddEvenMergeSort(CustomComponent):
    def __init__(self, n, explode=False):
        self.n = n
        inp = [Node() for _ in range(n)]
        out = [Node() for _ in range(n)]
        super().__init__(inp, out, "Sort" + str(n), explode=explode)

    def build(self):
        n, inp, out = self.n, self.inp, self.out
        if n == 1:
            inp >> out
        else:
            a = inp[:n // 2] >> OddEvenMergeSort(n // 2, explode=True)
            b = inp[n // 2:] >> OddEvenMergeSort(n // 2, explode=True)

            [a, b] >> OddEvenMerger(n // 2) >> out


num = 16
[Ground() >> DCVoltageSource(random.random()) for _ in range(num)] >> OddEvenMergeSort(num) >> [Resistor(1000) >> Ground() for i in range(num)]

spiceNetlist = CircuitEnv.compileSpiceNetlist('Sorter')
print(spiceNetlist)
f = open('/Users/tomerk/Desktop/sorter.cir', 'w')
f.write(spiceNetlist)
f.close()