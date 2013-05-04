from collections import defaultdict

#All three of these are temporarily replaced then restored when building a subcircuit
COMPONENTS = []
NODE_GRAPH = {}
TYPE_COUNT = defaultdict(int)

SUBCIRCUITS = {}
NODE_TYPE = '_NODE'

def connectedComponents(graph):
    def explore(node, net):
        if not node in netlist.keys():
            netlist[node] = net
            for nextNode in graph[node]:
                explore(nextNode, net)
    netlist = {}
    net = 0
    for node in sorted(graph.keys()):
        if net in netlist.values():
            net += 1
        explore(node, net)
    return netlist

def flatten(S):
    out = []
    for val in S:
        if hasattr(val, '__iter__') and not isinstance(val, str):
            out.extend(flatten(val))
        else:
            out.append(val)
    return out

class Connectable():
    def __rshift__(self, other):
        return connect(self, other)

    def __rrshift__(self, other):
        return connect(other, self)

def connect(fst, snd):
    if isinstance(fst, Node) and isinstance(snd, Node):
        # Connect two nodes
        num1 = fst.nodeNum
        num2 = snd.nodeNum

        # It needs to be an undirected graph so add both directions
        NODE_GRAPH[num1].add(num2)
        NODE_GRAPH[num2].add(num1)

        return AbstractComponent([fst], [snd])

    else:
        if isinstance(fst, Node):
            inp = [fst]
            fst = [fst]
        elif isinstance(fst, AbstractComponent):
            inp = fst.inp
            fst = fst.out
        else:
            inp = fst

        if isinstance(snd, Node):
            out = [snd]
            snd = [snd]
        elif isinstance(snd, AbstractComponent):
            out = snd.out
            snd = snd.inp
        else:
            out = snd

        for i, j in zip(fst, snd):
            connect(i, j)

        return AbstractComponent(inp, out)

class Node(Connectable):
    def __init__(self):
        self.nodeNum = TYPE_COUNT[NODE_TYPE]
        NODE_GRAPH[self.nodeNum] = set()
        TYPE_COUNT[NODE_TYPE] += 1

GROUND = Node()

class AbstractComponent(Connectable):
    # Try having base component __init__ to set self.inp and self.out so inp() and out() must be used to access?
    def __init__(self, inp, out):
        self.inp = Bundle(inp)
        self.out = Bundle(out)

class Component(AbstractComponent):
    def __init__(self, inp, out, name, attrs, connections=None):
        super().__init__(inp, out)
        idNum = TYPE_COUNT[name.upper()]
        TYPE_COUNT[name.upper()] += 1

        self.name = name.upper() + str(idNum)
        self.attrs = attrs
        self.connections = connections or flatten(self.inp + self.out)
        COMPONENTS.append((self.name, self.connections, self.attrs))#self)

class CustomComponent(Component):
    def __init__(self, inp, out, componentName):
        super().__init__(inp, out, 'x', [componentName])
        if not componentName in SUBCIRCUITS:
            global NODE_GRAPH
            global COMPONENTS
            global TYPE_COUNT

            prevNodeGraph = NODE_GRAPH
            prevComponents = COMPONENTS
            prevTypeCount = TYPE_COUNT

            NODE_GRAPH = {}
            COMPONENTS = []
            TYPE_COUNT = defaultdict(int)

            for node in [GROUND] + flatten(self.inp + self.out):
                NODE_GRAPH[node.nodeNum] = set()
                TYPE_COUNT[NODE_TYPE] = max(TYPE_COUNT[NODE_TYPE], node.nodeNum)

            SUBCIRCUITS[componentName] = (NODE_GRAPH, COMPONENTS, flatten(self.inp + self.out))
            self.build()

            NODE_GRAPH = prevNodeGraph
            COMPONENTS = prevComponents
            TYPE_COUNT = prevTypeCount

    def build(self):
        pass

class Bundle(list, Connectable):
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
