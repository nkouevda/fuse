from fuse.core import Component, Node, Model

class Resistor(Component):
    ''' Input is the positive node,
    Output is the negative node.
    '''
    def __init__(self, resistance, name = ''):
        Component.__init__(self, [Node()], [Node()], 'r' + name, [resistance])

class Capacitor(Component):
    ''' Input is the positive node,
    Output is the negative node.
    '''
    def __init__(self, capacitance, name = ''):
        Component.__init__(self, [Node()], [Node()], 'c' + name, [capacitance])

class Inductor(Component):
    ''' Input is the positive node,
    Output is the negative node.
    '''
    def __init__(self, inductance, name = ''):
        Component.__init__(self, [Node()], [Node()], 'l' + name, [inductance])

class CoupleInductors(Component):
    def __init__(self, inductor1, inductor2, coupling, name = ''):
        Component.__init__(self, [], [], 'k' + name, [inductor1.name, inductor2.name, coupling])

class Switch(Component):
    def __init__(self, model, name = ''):
        inp = [Node(), Node(), Node()]
        out = [Node()]
        Component.__init__(self, inp, out, 's' + name, [model.mname], connections = [inp[0], out[0], inp[1], inp[2]])

class CurrentSwitch(Component):
    def __init__(self, voltageSource, model, name = ''):
        Component.__init__(self, [Node()], [Node()], 'w' + name, [voltageSource.name, model.mname])

class SwitchModel(Model):
    def __init__(self, **kwargs):
        Model.__init__(self, 'sw', attrs=kwargs)

class VoltageSource(Component):
    ''' Input is the negative node,
        Output is the positive node '''
    def __init__(self, dc=0, ac=0, name = ''):
        inp, out = [Node()], [Node()]
        Component.__init__(self, inp, out, 'v' + name, ['dc', dc, 'ac', ac], connections=out+inp)

class DCVoltageSource(Component):
    def __init__(self, voltage, name = ''):
        VoltageSource.__init__(self, dc=voltage, name=name)

class ACVoltageSource(Component):
    def __init__(self, voltage, name = ''):
        VoltageSource.__init__(self, ac=voltage, name=name)

class CurrentSource(Component):
    ''' Input is the negative node,
        Output is the positive node '''
    def __init__(self, dc=0, ac=0, name = ''):
        inp, out = [Node()], [Node()]
        Component.__init__(self, inp, out, 'i' + name, ['dc', dc, 'ac', ac], connections=out+inp)

# Add dependent linear voltage + current sources
# Add nonlinear dependent voltage + current sources

## Transmission lines
# Lossless
# Lossy
# Distributed RC

## Transistors AND Diodes
# Junction Diodes
# BJTs
# JFETs
# MOSFETs
# MESFETs