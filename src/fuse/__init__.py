from collections import defaultdict

def singleton(cls):
    return cls()

@singleton
class CircuitEnv():
    def __init__(self):
        self.__frames = []
        self.__subcircuits = {}
        self.newFrame()

    def newFrame(self):
        self.curFrame = [{0: set()}, defaultdict(int), [], 1]
        self.__frames.append(self.curFrame)

    def storeFrameAsSubcircuit(self, name, connections):
        self.__subcircuits[name.upper()] = (connections, self.curFrame)

    def getSubcircuit(self, name):
        return self.__subcircuits.get(name.upper())

    def popFrame(self):
        self.curFrame = self.__frames[len(self.__frames) - 2]
        return self.__frames.pop()

    def newComponent(self, name, connections, attributes):
        name = name.upper()
        idNum = self.curFrame[1][name]
        self.curFrame[1][name] += 1

        component = (name + str(idNum), connections, attributes)
        self.curFrame[2].append(component)
        return name + str(idNum)

    def newNode(self):
        frame = self.curFrame
        nextNodeNum = frame[3]
        frame[3] += 1
        frame[0][nextNodeNum] = set()
        return nextNodeNum

    def connect(self, fst, snd):
        if isinstance(fst, Node) and isinstance(snd, Node):
            frame = self.curFrame

            # Connect two nodes
            num1 = fst.nodeNum
            num2 = snd.nodeNum

            # It needs to be an undirected graph so add both directions
            frame[0][num1].add(num2)
            frame[0][num2].add(num1)

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
                self.connect(i, j)

            return AbstractComponent(inp, out)

    def exportNetlist(self):
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

        nodeGraph = self.curFrame[0]
        components = self.curFrame[2]
        netlists = connectedComponents(nodeGraph)
        netlistString = ''
        for component in components:
            name = component[0]
            pins = [str(netlists[node]) for node in component[1]]
            attrs = [str(attr).upper() for attr in component[2]]

            netlistString += ' '.join([name] + pins + attrs) + '\n'

        return netlistString

class Connectable():
    def __rshift__(self, other):
        return CircuitEnv.connect(self, other)

    def __rrshift__(self, other):
        return CircuitEnv.connect(other, self)


class Node(Connectable):
    def __init__(self):
        self.nodeNum = CircuitEnv.newNode()

class Ground(Node):
    def __init__(self):
        self.nodeNum = 0

class Bundle(list, Connectable):
    # Make sure Bundles are returned from interactions w/ lists,
    # So the Connectable connections syntax may still be used
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
        connections = flattenNodes(connections) or flattenNodes(self.inp + self.out)
        self.name = CircuitEnv.newComponent(name, connections, attrs)

class CustomComponent(Component):
    def __init__(self, inp, out, componentName):
        super().__init__(inp, out, 'x', [componentName])
        if not CircuitEnv.getSubcircuit(componentName):

            # Store the current circuit environment
            prevNodeNums = flattenNodes(self.inp + self.out)

            # Enter a new subcircuit environment for all new nodes,
            # components, and connections to be built in
            CircuitEnv.newFrame()
            for node in flatten(self.inp + self.out):
                node.nodeNum = Node().nodeNum

            # Build the subcircuit and store it
            self.build()
            CircuitEnv.storeFrameAsSubcircuit(componentName, flattenNodes(self.inp + self.out))

            # Restore the previous circuit environment
            CircuitEnv.popFrame()
            for num, node in zip(prevNodeNums, flatten(self.inp + self.out)):
                node.nodeNum = num

    def build(self):
        pass

# STILL TODO:
# primitive components
# allow imported subcircuits
# Add compilation -> netlist file