from fuse.core import *
from fuse.primitives import *

class Comparator(CustomComponent):
    def __init__(self):
        inp, out = [Node(), Node()], [Node(), Node()]
        super().__init__(inp, out, 'comparator')

    def build(self):
        self.inp >> [Resistor(1000), Resistor(1000)] >> self.out

class OddEvenMerger(CustomComponent):
    def __init__(self, n, explode=False):
        self.n = n
        inp = [[Node() for _ in range(n)], [Node() for _ in range(n)]]
        out = [Node() for _ in range(2 * n)]
        componentName = 'merge' + str(n) + 'nums'
        super().__init__(inp, out, componentName, explode=explode)

    def build(self):
        n, inp, out = self.n, self.inp, self.out
        if n == 1:
            inp >> Comparator() >> out
        else:
            odd = inp[0][1::2], inp[1][1::2]
            odd_merger = odd >> OddEvenMerger(n // 2, explode=True)
            odd_merger.out[0] >> out[0]

            even = inp[0][::2], inp[1][::2]
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
        super().__init__(inp, out, "MergeSort" + str(n), explode=explode)

    def build(self):
        n, inp, out = self.n, self.inp, self.out
        if n == 1:
            inp >> out
        else:
            a = inp[:n // 2] >> OddEvenMergeSort(n // 2, explode=True)
            b = inp[n // 2:] >> OddEvenMergeSort(n // 2, explode=True)

            [a, b] >> OddEvenMerger(n // 2) >> out

OddEvenMergeSort(8)

print(CircuitEnv.compileSpiceNetlist('Sorter'))