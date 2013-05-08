from fuse.core import Component, Node

class Resistor(Component):
    def __init__(self, resistance, name = ''):
        Component.__init__(self, [Node()], [Node()], 'r' + name, [resistance])

class Capacitor(Component):
    def __init__(self, capacitance, name = ''):
        Component.__init__(self, [Node()], [Node()], 'c' + name, [capacitance])

class Inductor(Component):
    def __init__(self, inductance, name = ''):
        Component.__init__(self, [Node()], [Node()], 'l' + name, [inductance])

class CoupleInductors(Component):
    def __init__(self, inductor1, inductor2, coupling, name = ''):
        Component.__init__(self, [], [], 'k' + name, [inductor1.name, inductor2.name, coupling])

