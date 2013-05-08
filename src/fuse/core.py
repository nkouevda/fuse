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
        # Frame = nodeGraph, componentTypeCount, components, nextNodeNum,
        self.curFrame = [{0: set()}, defaultdict(int), [], 1]
        self.__frames.append(self.curFrame)

    def storeFrameAsSubcircuit(self, name, connections):
        assert len(self.curFrame[2]) != 0, name.upper() + " is empty"
        self.__subcircuits[name.upper()] = (connections, self.curFrame)

    def hasSubcircuit(self, name):
        return name.upper() in self.__subcircuits

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

    def frameSpiceNetlist(self, frame):
        def connectedComponents(graph):
            def explore(node, net):
                if not node in netlist:
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

        nodeGraph = frame[0]
        components = frame[2]
        netlists = connectedComponents(nodeGraph)
        netlistString = ''
        for component in components:
            name = component[0]
            pins = [str(netlists[node]) for node in component[1]]
            attrs = [str(attr).upper() for attr in component[2]]

            netlistString += ' '.join([name] + pins + attrs) + '\n'

        return netlistString, netlists

    def compileSpiceNetlist(self, name):
        out = name + '\n'
        globalNetlist, nodeNetlists = self.frameSpiceNetlist(self.curFrame)
        out += globalNetlist
        for name, subcircuit in self.__subcircuits.items():
            subcircuitNetlist, nodeNetlists = self.frameSpiceNetlist(subcircuit[1])
            pins = [str(nodeNetlists[node]) for node in subcircuit[0]]
            assert len(pins) == len(set(pins)), \
                "Component " + name + " has pins connected to the same netlist"
            out += '.SUBCKT ' + ' '.join([name] + pins) + '\n'
            out += subcircuitNetlist
            out += '.ENDS\n'

        out += '.op\n.end'
        return out

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
        return Bundle(list.copy(self))

    def __mul__(self, other):
        return Bundle(list.__mul__(self, other))

    def __rmul__(self, other):
        return Bundle(list.__rmul__(self, other))

    def __add__(self, other):
        return Bundle(list.__add__(self, other))

    def __radd__(self, other):
        return Bundle(list.__add__(self, other))

    def __getitem__(self, other):
        x = list.__getitem__(self, other)
        return Bundle(x) if isinstance(x, list) else x

class Bus(Bundle):
    def __init__(self, num):
        Bundle.__init__(self, [Node() for _ in range(num)])

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
        AbstractComponent.__init__(self, inp, out)
        connections = flattenNodes(connections) or flattenNodes(self.inp + self.out)
        self.name = CircuitEnv.newComponent(name, connections, attrs)

class CustomComponent(Component):
    def __init__(self, inp, out, componentName, explode=False):
        # If explode is False, a subcircuit is used for this component,
        # Otherwise it simply uses the connections as usual.
        if explode:
            AbstractComponent.__init__(self, inp, out)
            self.build()
        else:
            Component.__init__(self, inp, out, 'x' + componentName, [componentName])
            if not CircuitEnv.hasSubcircuit(componentName):

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
        # models
        # allow imported subcircuits?
        # node probing + transient analysis