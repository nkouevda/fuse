# Tomer Kaftan, Nikita Kouevda, Daniel Wong
# 2013/05/12

from collections import defaultdict


# Circuit Environment

def singleton(cls):
    return cls()


@singleton
class CircuitEnv():
    def __init__(self):
        self._frames = []
        self._subcircuits = {}
        self.new_frame()

    def new_frame(self):
        # node_graph, component_types, components, next_node_num
        self.current_frame = [{0: set()}, defaultdict(int), [], 1]
        self._frames.append(self.current_frame)

    def store_frame_as_subcircuit(self, name, connections):
        assert len(self.current_frame[2]) != 0, name.upper() + ' is empty'

        self._subcircuits[name.upper()] = (connections, self.current_frame)

    def has_subcircuit(self, name):
        return name.upper() in self._subcircuits

    def pop_frame(self):
        self.current_frame = self._frames[len(self._frames) - 2]

        return self._frames.pop()

    def new_component(self, name, connections, attributes):
        name = name.upper()
        idNum = self.current_frame[1][name]
        self.current_frame[1][name] += 1

        component = (name + str(idNum), connections, attributes)
        self.current_frame[2].append(component)

        return name + str(idNum)

    def new_node(self):
        frame = self.current_frame
        next_node_num = frame[3]
        frame[3] += 1
        frame[0][next_node_num] = set()

        return next_node_num

    def connect(self, first, second):
        if isinstance(first, Node) and isinstance(second, Node):
            frame = self.current_frame

            # Connect two nodes
            num1 = first.node_num
            num2 = second.node_num

            # It needs to be an undirected graph so add both directions
            frame[0][num1].add(num2)
            frame[0][num2].add(num1)

            return AbstractComponent([first], [second])
        else:
            if isinstance(first, Node):
                inp = [first]
                first = [first]
            elif isinstance(first, AbstractComponent):
                inp = first.inp
                first = first.out
            else:
                inp = first

            if isinstance(second, Node):
                out = [second]
                second = [second]
            elif isinstance(second, AbstractComponent):
                out = second.out
                second = second.inp
            else:
                out = second

            for i, j in zip(first, second):
                self.connect(i, j)

            return AbstractComponent(inp, out)

    def frame_spice_netlist(self, frame):
        def connected_components(graph):
            def explore(node, net):
                if node not in netlist:
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

        node_graph = frame[0]
        components = frame[2]
        netlists = connected_components(node_graph)
        netlist_str = ''

        for component in components:
            name = component[0]
            pins = [str(netlists[node]) for node in component[1]]
            attrs = [str(attr).upper() for attr in component[2]]
            netlist_str += ' '.join([name] + pins + attrs) + '\n'

        return netlist_str, netlists

    def compile_spice_netlist(self, name):
        out = name + '\n'
        global_netlist, node_netlists = self.frame_spice_netlist(
            self.current_frame)
        out += global_netlist

        for name, subcircuit in self._subcircuits.items():
            subcircuit_netlist, node_netlists = self.frame_spice_netlist(
                subcircuit[1])
            pins = [str(node_netlists[node]) for node in subcircuit[0]]

            assert len(pins) == len(set(pins)), \
                'Component ' + name + ' has pins connected to the same netlist'

            out += '.SUBCKT ' + ' '.join([name] + pins) + '\n'
            out += subcircuit_netlist + '.ENDS\n'

        out += '.op\n.end'

        return out


# Core

def flatten(iterable):
    """Return the flattened version of the given iterable."""

    out = []

    for val in iterable if iterable else []:
        if hasattr(val, '__iter__') and not isinstance(val, str):
            out.extend(flatten(val))
        else:
            out.append(val)

    return out


def flatten_node_nums(nodes):
    """Return the node numbers of the flattened version of the given nodes."""

    return [node.node_num for node in flatten(nodes)]


class Connectable():
    """The base class for fuse objects.

    Implement the ability to connect to other Connectable objects via >> or <<.
    """

    def __rshift__(self, other):
        return CircuitEnv.connect(self, other)

    def __rrshift__(self, other):
        return CircuitEnv.connect(other, self)

    def __lshift__(self, other):
        return CircuitEnv.connect(other, self)

    def __rlshift__(self, other):
        return CircuitEnv.connect(self, other)


class Node(Connectable):
    """The node class for fuse objects.

    A connection points to a netlist within the circuit.
    """

    def __init__(self):
        self.node_num = CircuitEnv.new_node()


class Ground(Node):
    """The ground class for fuse objects.

    Represent the zero-voltage section of a circuit; node_num is always 0.
    """

    def __init__(self):
        self.node_num = 0


class Bus(list, Connectable):
    """The bus class for fuse objects.

    Represent a sequence of nodes; extends list in order to allow iteration.
    """

    def __init__(self, num):
        list.__init__(self, [Node() for _ in range(num)])


class AbstractComponent(Connectable):
    """The abstract component class for fuse objects.

    Use self.inp and self.out for input and output, respectively.
    """

    def __init__(self, inp, out):
        self.inp = inp
        self.out = out


class Component(AbstractComponent):
    """The component class for fuse objects.

    The connections parameter allows interaction with the SPICE netlist.
    Constructing a component will add the component to the current frame.
    """

    def __init__(self, inp, out, name, attrs, connections=None):
        AbstractComponent.__init__(self, inp, out)
        connections = (
            flatten_node_nums(connections)
            or flatten_node_nums(self.inp + self.out))
        self.name = CircuitEnv.new_component(name, connections, attrs)


class Model(Component):
    """The model class for fuse objects.

    Allow for the use of specific models of various components, for SPICE
    compatibility.
    """

    def __init__(self, component_type, attrs=dict()):
        mname = '.model ' + component_type + 'model'
        attrsStringList = [str(i) + '=' + str(j) for i, j in attrs.items()]
        Component.__init__(
            self, [], [], mname, [component_type] + attrsStringList)

        # Remove the '.model ' from the name
        self.mname = self.name[7:]


class CustomComponent(Component):
    """The custom component class for fuse objects.

    Allow for the impmlementation of subcircuits as single fuse components.
    """

    def __init__(self, inp, out, componentName, explode=False):
        # Do not use a subcircuit for this component if explode is True
        if explode:
            AbstractComponent.__init__(self, inp, out)
            self.build()
        else:
            Component.__init__(
                self, inp, out, 'X' + componentName, [componentName])

            if not CircuitEnv.has_subcircuit(componentName):
                # Store the current circuit environment
                prev_nums = flatten_node_nums(self.inp + self.out)

                # Enter a new subcircuit environment for all new nodes,
                # components, and connections to be built in
                CircuitEnv.new_frame()

                for node in flatten(self.inp + self.out):
                    node.node_num = Node().node_num

                # Build the subcircuit and store it
                self.build()
                CircuitEnv.store_frame_as_subcircuit(
                    componentName, flatten_node_nums(self.inp + self.out))

                # Restore the previous circuit environment
                CircuitEnv.pop_frame()

                for num, node in zip(prev_nums, flatten(self.inp + self.out)):
                    node.node_num = num


# SPICE Primitives

# R
class Resistor(Component):
    """Resistor.

    Input: the + node.
    Output: the - node.
    """

    def __init__(self, resistance, name=''):
        Component.__init__(self, [Node()], [Node()], 'R' + name, [resistance])


# C
class Capacitor(Component):
    """Capacitor.

    Input: the + node.
    Output: the - node.
    """

    def __init__(self, capacitance, name=''):
        Component.__init__(self, [Node()], [Node()], 'C' + name, [capacitance])


# L
class Inductor(Component):
    """Inductor.

    Input: the + node.
    Output: the - node.
    """

    def __init__(self, inductance, name=''):
        Component.__init__(self, [Node()], [Node()], 'L' + name, [inductance])


# K
class CoupledInductors(Component):
    def __init__(self, inductor1, inductor2, coupling, name=''):
        Component.__init__(
            self, [], [], 'K' + name,
            [inductor1.name, inductor2.name, coupling])


# S
class Switch(Component):
    """Switch.

    Input: the + terminal, the + voltage reference, the - voltage reference.
    Output: the - terminal.
    """

    def __init__(self, model, name=''):
        inp = [Node(), Node(), Node()]
        out = [Node()]

        Component.__init__(
            self, inp, out, 'S' + name, [model.mname],
            connections=[inp[0], out[0], inp[1], inp[2]])


# W
class CurrentSwitch(Component):
    """Current switch.

    Input: the + terminal.
    Output: the - terminal.

    The reference current is the current through the input voltage source.
    """

    def __init__(self, source, model, name=''):
        Component.__init__(
            self, [Node()], [Node()], 'W' + name,
            [source.name, model.mname])


# SW
class SwitchModel(Model):
    def __init__(self, **kwargs):
        Model.__init__(self, 'SW', attrs=kwargs)


# CSW
class CurrentSwitchModel(Model):
    def __init__(self, **kwargs):
        Model.__init__(self, 'CSW', attrs=kwargs)


# V
class VoltageSource(Component):
    """Voltage source.

    Input: the + node.
    Output: the - node.
    """

    def __init__(self, dc=0, ac=0, name=''):
        inp, out = [Node()], [Node()]
        Component.__init__(
            self, inp, out, 'V' + name, ['DC', dc, 'AC', ac],
            connections=out + inp)


# DC
class DCVoltageSource(VoltageSource):
    def __init__(self, voltage, name=''):
        VoltageSource.__init__(self, dc=voltage, name=name)


# AC
class ACVoltageSource(VoltageSource):
    def __init__(self, voltage, name=''):
        VoltageSource.__init__(self, ac=voltage, name=name)


# I
class CurrentSource(Component):
    """Current source.

    Input: the + node.
    Output: the - node.
    """

    def __init__(self, dc=0, ac=0, name=''):
        inp, out = [Node()], [Node()]

        Component.__init__(
            self, inp, out, 'I' + name, ['DC', dc, 'AC', ac],
            connections=out + inp)


# E
class VCVS(Component):
    """Voltage-controlled voltage source.

    Input: the + terminal, the + voltage reference, the - voltage reference.
    Output: the - terminal.
    """

    def __init__(self, multiplier, name=''):
        inp = [Node(), Node(), Node()]
        out = [Node()]
        Component.__init__(
            self, inp, out, 'E' + name, [multiplier],
            connections=[inp[0], out[0], inp[1], inp[2]])


# F
class CCCS(Component):
    """Current-controlled current source.

    Input: the + terminal.
    Output: the - terminal.

    The reference current is the current through the input voltage source.
    """

    def __init__(self, source, multiplier, name=''):
        Component.__init__(
            self, [Node()], [Node()], 'F' + name,
            [source.name, multiplier])


# G
class VCCS(Component):
    """Voltage-controlled current source.

    Input: the + terminal, the + voltage reference, the - voltage reference.
    Output: the - terminal.
    """

    def __init__(self, multiplier, name=''):
        inp = [Node(), Node(), Node()]
        out = [Node()]

        Component.__init__(
            self, inp, out, 'G' + name, [multiplier],
            connections=[inp[0], out[0], inp[1], inp[2]])


# H
class CCVS(Component):
    """Current-controlled voltage source.

    Input: the + terminal.
    Output: the - terminal.

    The reference current is the current through the input voltage source.
    """

    def __init__(self, source, multiplier, name=''):
        Component.__init__(
            self, [Node()], [Node()], 'H' + name, [source.name, multiplier])


# D
class Diode(Component):
    """Diode.

    Input: the + terminal.
    Output: the - terminal.

    The reference current is the current through the input voltage source.
    """

    def __init__(self, model, name=''):
        Component.__init__(self, [Node()], [Node()], 'D' + name, [model.mname])


# D
class DiodeModel(Model):
    def __init__(self, **kwargs):
        Model.__init__(self, 'D', attrs=kwargs)


# Q
class BJT(Component):
    """Bipolar junction transistor.

    Input: the collector node, the base node.
    Output: the emitter node.
    """

    def __init__(self, model, name=''):
        Component.__init__(
            self, [Node(), Node()], [Node()], 'Q' + name, [model.mname])


# NPN, PNP
class BJTModel(Model):
    def __init__(self, npn, **kwargs):
        Model.__init__(self, 'NPN' if npn else 'PNP', attrs=kwargs)


# J
class JFET(Component):
    """Junction gate field-effect transistor.

    Input: the drain node, the gate node.
    Output: the source node.
    """

    def __init__(self, model, name=''):
        Component.__init__(
            self, [Node(), Node()], [Node()], 'J' + name, [model.mname])


# NJF, PJF
class JFETModel(Model):
    def __init__(self, njf, **kwargs):
        Model.__init__(self, 'NJF' if njf else 'PJF', attrs=kwargs)


# M
class MOSFET(Component):
    """Metal-oxide- semiconductor field-effect transistor.

    Input: the drain node, the gate node.
    Output: the source node, the bulk node.
    """

    def __init__(self, model, name=''):
        Component.__init__(
            self, [Node(), Node()], [Node(), Node()], 'M' + name,
            [model.mname])


# NMOS, PMOS
class MOSFETModel(Model):
    def __init__(self, nmos, **kwargs):
        Model.__init__(self, 'NMOS' if nmos else 'PMOS', attrs=kwargs)


# Z
class MESFET(Component):
    """Metal semiconductor field effect transistor.

    Input: the drain node, the gate node.
    Output: the source node.

    """

    def __init__(self, model, name=''):
        Component.__init__(
            self, [Node(), Node()], [Node()], 'Z' + name, [model.mname])


# NMF, PMF
class MESFETModel(Model):
    def __init__(self, nmf, **kwargs):
        Model.__init__(self, 'NMF' if nmf else 'PMF', attrs=kwargs)
