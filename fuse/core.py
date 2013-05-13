# Tomer Kaftan, Nikita Kouevda, Daniel Wong
# 2013/05/12

from collections import defaultdict


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


class Connectable():
    def __rshift__(self, other):
        return CircuitEnv.connect(self, other)

    def __rrshift__(self, other):
        return CircuitEnv.connect(other, self)


class Node(Connectable):
    def __init__(self):
        self.node_num = CircuitEnv.new_node()


class Ground(Node):
    def __init__(self):
        self.node_num = 0


class Bus(list, Connectable):
    def __init__(self, num):
        list.__init__(self, [Node() for _ in range(num)])


class AbstractComponent(Connectable):
    def __init__(self, inp, out):
        self.inp = inp
        self.out = out


def flatten_nodes(nodes):
    return [node.node_num for node in flatten(nodes)]


def flatten(iterable):
    out = []

    for val in iterable if iterable else []:
        if hasattr(val, '__iter__') and not isinstance(val, str):
            out.extend(flatten(val))
        else:
            out.append(val)

    return out


class Component(AbstractComponent):
    def __init__(self, inp, out, name, attrs, connections=None):
        AbstractComponent.__init__(self, inp, out)
        connections = (
            flatten_nodes(connections) or flatten_nodes(self.inp + self.out))
        self.name = CircuitEnv.new_component(name, connections, attrs)


class Model(Component):
    def __init__(self, component_type, attrs=dict()):
        mname = '.model ' + component_type + 'model'
        attrsStringList = [str(i) + '=' + str(j) for i, j in attrs.items()]
        Component.__init__(
            self, [], [], mname, [component_type] + attrsStringList)

        # Remove the '.model ' from the name
        self.mname = self.name[7:]


class CustomComponent(Component):
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
                prev_node_nums = flatten_nodes(self.inp + self.out)

                # Enter a new subcircuit environment for all new nodes,
                # components, and connections to be built in
                CircuitEnv.new_frame()

                for node in flatten(self.inp + self.out):
                    node.node_num = Node().node_num

                # Build the subcircuit and store it
                self.build()
                CircuitEnv.store_frame_as_subcircuit(
                    componentName, flatten_nodes(self.inp + self.out))

                # Restore the previous circuit environment
                CircuitEnv.pop_frame()

                flattened = flatten(self.inp + self.out)

                for num, node in zip(prev_node_nums, flattened):
                    node.node_num = num
