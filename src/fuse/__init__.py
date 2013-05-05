from collections import defaultdict

#NODE_GRAPH, TYPE_COUNT, and COMPONENTS are temporarily replaced then restored when building a subcircuit
NODE_GRAPH = {}
TYPE_COUNT = defaultdict(int)
COMPONENTS = []

SUBCIRCUITS = {}
IMPORTED = []
NODE_TYPE = '_NODE'

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

class AbstractComponent(Connectable):
    # Try having base component __init__ to set self.inp and self.out so inp() and out() must be used to access?
    def __init__(self, inp, out):
        self.inp = Bundle(inp)
        self.out = Bundle(out)

def flattenNodes(S):
    return [node.nodeNum for node in flatten(S)]

def flatten(S):
    out = []
    for val in S if S else []:
        if hasattr(val, '__iter__') and not isinstance(val, str):
            out.extend(flatten(val))
        else:
            out.append(val)
    return out

class Component(AbstractComponent):
    def __init__(self, inp, out, name, attrs, connections=None):
        super().__init__(inp, out)
        idNum = TYPE_COUNT[name.upper()]
        TYPE_COUNT[name.upper()] += 1

        self.name = name.upper() + str(idNum)
        self.attrs = attrs
        self.connections = flattenNodes(connections) or flattenNodes(self.inp + self.out)
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
            prevNodeNums = flattenNodes(self.inp + self.out)
            for i, node in enumerate(flatten(self.inp + self.out)):
                node.nodeNum = i + 1

            NODE_GRAPH = {}
            COMPONENTS = []
            TYPE_COUNT = defaultdict(int)

            numIO = len(flatten(self.inp + self.out))
            for node in range(numIO + 1):
                NODE_GRAPH[node] = set()
            TYPE_COUNT[NODE_TYPE] = numIO + 1

            SUBCIRCUITS[componentName] = (NODE_GRAPH, COMPONENTS, flattenNodes(self.inp + self.out))
            self.build()

            NODE_GRAPH = prevNodeGraph
            COMPONENTS = prevComponents
            TYPE_COUNT = prevTypeCount
            for num, node in zip(prevNodeNums, flatten(self.inp + self.out)):
                node.nodeNum = num

    def build(self):
        pass

# STILL TODO:
# primitive components
# allow imported subcircuits
# Add compilation -> netlist file

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