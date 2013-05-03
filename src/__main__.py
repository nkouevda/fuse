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
            [self.getInput()[0][0], self.getInput()[1][0]] >> Comparator(bits) >> self.getOutput()
        else:
            odd = self.getInput()[0][1::2], self.getInput()[1][1::2]
            odd_merger = odd >> OddEvenMerger(n // 2, bits)
            odd_merger.getOutput()[0] >> self.getOutput()[0]


            even = self.input[0][::2], self.input[1][::2]
            even_merger = even >> OddEvenMerger(n // 2, bits)
            even_merger.getOutput()[n - 1] >> self.getOutput()[2 * n - 1]

            for i in range(n - 1):
                ([odd_merger.getOutput()[i + 1], even_merger.getOutput()[i]]
                 >> Comparator(bits) >> [self.getOutput()[2 * i + 1], self.getOutput()[2 * i + 2]])

class OddEvenMergeSort(Component):
    def __init__(self, n, bits):
        self.input = [Bus(bits) for _ in range(n)]
        self.output = [Bus(bits) for _ in range(n)]

        if n == 1:
            self.getInput() >> self.getOutput()
        else:
            a = self.getInput()[:n // 2] >> OddEvenMergeSort(n // 2, bits)
            b = self.getInput()[n // 2:] >> OddEvenMergeSort(n // 2, bits)

            [a, b] >> OddEvenMerger(n // 2, bits) >> self.getOutput()

x = OddEvenMergeSort(32, 8)

print(NODE_GRAPH)