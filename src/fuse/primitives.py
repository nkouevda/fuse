from fuse.core import Component, Node

class Resistor(Component):
    def __init__(self, resistance, name = ''):
        Component.__init__(self, [Node()], [Node()], 'r' + name, [resistance])
