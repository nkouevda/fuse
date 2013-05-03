NODE_GRAPH = {}
COMPONENTS = []

def connect(fst, snd):
    if isinstance(fst, Node) and isinstance(snd, Node):
        # Connect two nodes
        num1 = fst.nodeNum
        num2 = snd.nodeNum

        # It needs to be an undirected graph so add both directions
        NODE_GRAPH[num1].add(num2)
        NODE_GRAPH[num2].add(num1)

        return Component([fst], [snd])

    else:
        if isinstance(fst, Node):
            inp = [fst]
            fst = [fst]
        elif isinstance(fst, Component):
            inp = fst.inp
            fst = fst.out
        else:
            inp = fst

        if isinstance(snd, Node):
            out = [snd]
            snd = [snd]
        elif isinstance(snd, Component):
            out = snd.out
            snd = snd.inp
        else:
            out = snd

        for i, j in zip(fst, snd):
            connect(i, j)

        return Component(inp, out)

_nextNum = 0
class Node():
    def __init__(self):
        global _nextNum
        self.nodeNum = _nextNum
        NODE_GRAPH[_nextNum] = set()
        _nextNum += 1

    def __rshift__(self, other):
        return connect(self, other)

GROUND = Node()

class Component():
    # Try having base component __init__ to set self.inp and self.out so inp() and out() must be used to access?
    def __init__(self, inp, out):
        self.inp = Bundle(inp)
        self.out = Bundle(out)

    def __rshift__(self, other):
        return connect(self, other)

    def __rrshift__(self, other):
        return connect(other, self)

class Bundle(list):
    def __rshift__(self, other):
        return connect(self, other)

    def __rrshift__(self, other):
        return connect(other, self)

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
