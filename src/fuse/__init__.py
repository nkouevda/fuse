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

        return ConnectedComponentsWrapper(self, other)

GROUND = Node()

class Component():
    def getInput(self):
        return self.input

    def getOutput(self):
        return self.output

    def __rshift__(self, other):
        self.output >> other
        return ConnectedComponentsWrapper(self, other)

class ConnectedComponentsWrapper(Component):
    def __init__(self, input, output):
        """
        Takes two components as input, and sets the input of one as the input
        to this component, and the output of the other as the output for this
        component.
        :param input: This will be treated as the input for this component
        :param output: This will be treated as the output for this component
        """
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

        return ConnectedComponentsWrapper(self, other)

''' Wrap the output of all relevant list functions (e.g. slicing) with a Bundle
'''
def _listFuncWrapper(func):
    def newFunc(*args, **kwargs):
        out = func(*args, **kwargs)
        if not isinstance(out, Bundle) and isinstance(out, list):
            out = Bundle(out)
        return out
    return newFunc
for attr in list.__dict__:
    if callable(getattr(list, attr)):
        setattr(Bundle, attr, _listFuncWrapper(getattr(list, attr)))

class Bus(Bundle):
    def __init__(self, num):
        super().__init__([Node() for _ in range(num)])
