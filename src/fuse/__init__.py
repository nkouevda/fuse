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
        num2 = other.getInput().getNodeNum()

        # It needs to be an undirected graph so add both directions
        NODE_GRAPH[num1].add(num2)
        NODE_GRAPH[num2].add(num1)

        return ConnectedComponents(self, other)

GROUND = Node()

class Component():
    def getInput(self):
        return self.input

    def getOutput(self):
        return self.output

    def __rshift__(self, other):
        self.output >> other
        return ConnectedComponents(self, other)

class ConnectedComponents(Component):
    def __init__(self, input, output):
        self.input = input.getInput()
        self.output = output.getOutput()

class Bundle(list):
    def getInput(self):
        return self

    def getOutput(self):
        return self

    def __rshift__(self, other):
        for i, j in zip(self, other.getInput()):
            i >> j

        return ConnectedComponents(self, other)

def wrapFunctionWithListToBundle(func):
    def newFunc(*args, **kwargs):
        out = func(*args, **kwargs)
        if not isinstance(out, Bundle) and isinstance(out, list):
            out = Bundle(out)
        return out
    return newFunc

for attr in list.__dict__:
    if callable(getattr(list, attr)):
        setattr(Bundle, attr, wrapFunctionWithListToBundle(getattr(list, attr)))

class Bus(Bundle):
    def __init__(self, num):
        super().__init__([Node() for _ in range(num)])

bus1 = Bus(4) >> Bus(4)[:5].copy()

print(NODE_GRAPH)