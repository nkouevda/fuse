NODE_GRAPH = {}
COMPONENTS = []

_nextNum = 0
class Node():
    def __init__(self):
        global _nextNum
        self.__node_num__ = _nextNum
        NODE_GRAPH[_nextNum] = set()
        _nextNum += 1

    def getNodeNum(self):
        return self.__node_num__

    def getInput(self):
        return self

    def getOutput(self):
        return self

    def __rshift__(self, other):
        num1 = self.getNodeNum()
        num2 = other.getNodeNum()

        # It needs to be an undirected graph so add both directions
        NODE_GRAPH[num1].add(num2)
        NODE_GRAPH[num2].add(num1)

        return IOComponentWrapper(self, other)

GROUND = Node()

class Component():
    def getInput(self):
        return Bundle(self.input)

    def getOutput(self):
        return Bundle(self.output)

    def __rshift__(self, other):
        if (isinstance(other, Node)):
            self.getOutput()[0] >> other
            return IOComponentWrapper(self.getInput(), [other])
        elif isinstance(other, Component):
            for i, j in zip(self.getOutput(), other.getInput()):
                try:
                    i = Bundle(i)
                except TypeError:
                    pass
                try:
                    j = Bundle(j)
                except TypeError:
                    pass
                i >> j
            return IOComponentWrapper(self.getInput(), other.getOutput())
        else:
            for i, j in zip(self.getOutput(), other):
                try:
                    i = Bundle(i)
                except TypeError:
                    pass
                try:
                    j = Bundle(j)
                except TypeError:
                    pass
                i >> j
            return IOComponentWrapper(self.getInput(), other)

    def __rrshift__(self, other):
        if (isinstance(other, Node)):
            other >> self.getInput()[0]
            return IOComponentWrapper([other], self.getOutput())
        elif isinstance(other, Component):
            for i, j in zip(other.getOutput(), self.getInput()):
                try:
                    i = Bundle(i)
                except TypeError:
                    pass
                try:
                    j = Bundle(j)
                except TypeError:
                    pass
                i >> j
            return IOComponentWrapper(other.getInput(), self.getOutput())
        else:
            for i, j in zip(other, self.getInput()):
                try:
                    i = Bundle(i)
                except TypeError:
                    pass
                try:
                    j = Bundle(j)
                except TypeError:
                    pass
                i >> j
            return IOComponentWrapper(other, self.getOutput())

class IOComponentWrapper(Component):
    def __init__(self, input, output):
        self.input = input
        self.output = output

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
