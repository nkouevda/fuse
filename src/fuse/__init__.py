NODE_GRAPH = {}
COMPONENTS = []

_nextNum = 0
class Node():
    def __init__(self):
        global _nextNum
        self.nodeNum = _nextNum
        NODE_GRAPH[_nextNum] = set()
        _nextNum += 1

    def __rshift__(self, other):
        num1 = self.nodeNum
        num2 = other.nodeNum

        # It needs to be an undirected graph so add both directions
        NODE_GRAPH[num1].add(num2)
        NODE_GRAPH[num2].add(num1)

        return IOComponentWrapper([self], [other])

GROUND = Node()

class Component():
    def getInput(self):
        return Bundle(self.input)

    def getOutput(self):
        return Bundle(self.output)

    def bundleIfIterables(self, i, j):
        try:
            i = Bundle(i)
        except TypeError:
            pass
        try:
            j = Bundle(j)
        except TypeError:
            pass
        return i, j

    def __rshift__(self, other):
        if isinstance(other, Node):
            self.getOutput()[0] >> other
            return IOComponentWrapper(self.getInput(), [other])
        elif isinstance(other, Component):
            for i, j in zip(self.getOutput(), other.getInput()):
                i, j = self.bundleIfIterables(i, j)
                i >> j
            return IOComponentWrapper(self.getInput(), other.getOutput())
        else:
            for i, j in zip(self.getOutput(), other):
                i, j = self.bundleIfIterables(i, j)
                i >> j
            return IOComponentWrapper(self.getInput(), other)

    def __rrshift__(self, other):
        if isinstance(other, Node):
            other >> self.getInput()[0]
            return IOComponentWrapper([other], self.getOutput())
        elif isinstance(other, Component):
            for i, j in zip(other.getOutput(), self.getInput()):
                i, j = self.bundleIfIterables(i, j)
                i >> j
            return IOComponentWrapper(other.getInput(), self.getOutput())
        else:
            for i, j in zip(other, self.getInput()):
                i, j = self.bundleIfIterables(i, j)
                i >> j
            return IOComponentWrapper(other, self.getOutput())

class IOComponentWrapper(Component):
    def __init__(self, inp, out):
        self.input = inp
        self.output = out

class Bundle(Component, list):
    def getInput(self):
        return self

    def getOutput(self):
        return self

    # Make sure Bundles are returned from interactions w/ lists
    def copy(self):
        return Bundle(super().copy())

    def __mul__(self, other):
        return Bundle(super().__mul__(other))

    def __rmul__(self, other):
        return Bundle(super().__rmul__(other))

    def __add__(self, other):
        return Bundle(super().__add__(other))

    def __radd__(self, other):
        return Bundle(super().__add__(other))

    def __getitem__(self, other):
        x = super().__getitem__(other)
        return Bundle(x) if isinstance(x, list) else x

class Bus(Bundle):
    def __init__(self, num):
        super().__init__([Node() for _ in range(num)])
