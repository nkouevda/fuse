from fuse import *

class Comparator(CustomComponent):
    def __init__(self, bits):
        inp = [Bus(bits), Bus(bits)]
        out = [Bus(bits), Bus(bits)]
        self.bits = bits
        super().__init__(inp, out, 'comparator' + str(bits))

    def build(self):
        self.inp >> [[Resistor(1000) for _ in range(self.bits)], [Resistor(1000) for _ in range(self.bits)]] >> self.out

class OddEvenMerger(CustomComponent):
    def __init__(self, n, bits):
        self.n, self.bits = n, bits
        inp = [[Bus(bits) for _ in range(n)], [Bus(bits) for _ in range(n)]]
        out = [Bus(bits) for _ in range(2 * n)]
        componentName = 'merge' + str(n) + 'nums' + str(bits) + "bits"
        super().__init__(inp, out, componentName)

    def build(self):
        n, bits, inp, out = self.n, self.bits, self.inp, self.out
        if n == 1:
            [inp[0][0], self.inp[1][0]] >> Comparator(bits) >> out
        else:
            odd = inp[0][1::2], inp[1][1::2]
            odd_merger = odd >> OddEvenMerger(n // 2, bits)
            odd_merger.out[0] >> out[0]

            even = inp[0][::2], inp[1][::2]
            even_merger = even >> OddEvenMerger(n // 2, bits)
            even_merger.out[n - 1] >> out[2 * n - 1]

            for i in range(n - 1):
                ([odd_merger.out[i + 1], even_merger.out[i]]
                 >> Comparator(bits) >> [out[2 * i + 1], out[2 * i + 2]])

class OddEvenMergeSort(AbstractComponent):
    def __init__(self, n, bits):
        inp = [Bus(bits) for _ in range(n)]
        out = [Bus(bits) for _ in range(n)]
        super().__init__(inp, out)

        if n == 1:
            self.inp >> self.out
        else:
            a = self.inp[:n // 2] >> OddEvenMergeSort(n // 2, bits)
            b = self.inp[n // 2:] >> OddEvenMergeSort(n // 2, bits)

            [a, b] >> OddEvenMerger(n // 2, bits) >> self.out

OddEvenMergeSort(8, 4)

print(CircuitEnv.compileSpiceNetlist('Sorter'))