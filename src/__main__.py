from fuse import *


class Comparator(Component):
    def __init__(self, bits):
        self.input = [Bus(bits), Bus(bits)]
        self.output = [Bus(bits), Bus(bits)]

class OddEvenMerger(Component):
    def __init__(self, n, bits):
        self.input = [[Bus(bits) for _ in range(n)], [Bus(bits) for _ in range(n)]]
        self.output = [Bus(bits) for _ in range(2 * n)]

        if n == 1:
            [self.inp()[0][0], self.inp()[1][0]] >> Comparator(bits) >> self.out()
        else:
            odd = self.inp()[0][1::2], self.inp()[1][1::2]
            odd_merger = odd >> OddEvenMerger(n // 2, bits)
            odd_merger.out()[0] >> self.out()[0]

            even = self.inp()[0][::2], self.inp()[1][::2]
            even_merger = even >> OddEvenMerger(n // 2, bits)
            even_merger.out()[n - 1] >> self.out()[2 * n - 1]

            for i in range(n - 1):
                ([odd_merger.out()[i + 1], even_merger.out()[i]]
                 >> Comparator(bits) >> [self.out()[2 * i + 1], self.out()[2 * i + 2]])

class OddEvenMergeSort(Component):
    def __init__(self, n, bits):
        self.input = [Bus(bits) for _ in range(n)]
        self.output = [Bus(bits) for _ in range(n)]

        if n == 1:
            self.inp() >> self.out()
        else:
            a = self.inp()[:n // 2] >> OddEvenMergeSort(n // 2, bits)
            b = self.inp()[n // 2:] >> OddEvenMergeSort(n // 2, bits)

            [a, b] >> OddEvenMerger(n // 2, bits) >> self.out()

x = OddEvenMergeSort(32, 8)

print(NODE_GRAPH)