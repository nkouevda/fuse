from fuse.core import Component, Node, Model

# The primitives do not include:
# nonlinear sources,
# transmission lines,
# optional primitive fields (models or otherwise)

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
    ''' Input is the positive terminal, the positive voltage reference, the negative voltage reference
    Output is the negative terminal'''
    def __init__(self, model, name = ''):
        inp = [Node(), Node(), Node()]
        out = [Node()]
        Component.__init__(self, inp, out, 's' + name, [model.mname], connections = [inp[0], out[0], inp[1], inp[2]])

class CurrentSwitch(Component):
    ''' Input is the positive terminal,
    Output is the negative terminal,
    The reference current is the current through the input voltage source'''
    def __init__(self, sourceWithCurrent, model, name = ''):
        Component.__init__(self, [Node()], [Node()], 'w' + name, [sourceWithCurrent.name, model.mname])

class SwitchModel(Model):
    def __init__(self, **kwargs):
        Model.__init__(self, 'sw', attrs=kwargs)

class CurrentSwitchModel(Model):
    def __init__(self, **kwargs):
        Model.__init__(self, 'csw', attrs=kwargs)

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

# linearly dependent voltage + current sources
class VoltageControlledCurrentSource(Component):
    ''' Input is the positive terminal, the positive voltage reference, the negative voltage reference
    Output is the negative terminal'''
    def __init__(self, multiplier, name = ''):
        inp = [Node(), Node(), Node()]
        out = [Node()]
        Component.__init__(self, inp, out, 'g' + name, [multiplier], connections = [inp[0], out[0], inp[1], inp[2]])

class VoltageControlledVoltageSource(Component):
    ''' Input is the positive terminal, the positive voltage reference, the negative voltage reference
    Output is the negative terminal'''
    def __init__(self, multiplier, name = ''):
        inp = [Node(), Node(), Node()]
        out = [Node()]
        Component.__init__(self, inp, out, 'e' + name, [multiplier], connections = [inp[0], out[0], inp[1], inp[2]])

class CurrentControlledCurrentSource(Component):
    ''' Input is the positive terminal,
    Output is the negative terminal,
    The reference current is the current through the input voltage source'''
    def __init__(self, sourceWithCurrent, multiplier, name = ''):
        Component.__init__(self, [Node()], [Node()], 'f' + name, [sourceWithCurrent.name, multiplier])

class CurrentControlledVoltageSource(Component):
    ''' Input is the positive terminal,
    Output is the negative terminal,
    The reference current is the current through the input voltage source'''
    def __init__(self, sourceWithCurrent, multiplier, name = ''):
        Component.__init__(self, [Node()], [Node()], 'h' + name, [sourceWithCurrent.name, multiplier])

## Transistors AND Diodes
# Junction Diodes
class Diode(Component):
    ''' Input is the positive terminal,
    Output is the negative terminal,
    The reference current is the current through the input voltage source'''
    def __init__(self, model, name = ''):
        Component.__init__(self, [Node()], [Node()], 'd' + name, [model.mname])

class DiodeModel(Model):
    def __init__(self, **kwargs):
        Model.__init__(self, 'd', attrs=kwargs)

# BJTs
class BJT(Component):
    ''' Input is the collector node, base node
    Output is the emitter node'''
    def __init__(self, model, name = ''):
        Component.__init__(self, [Node(), Node()], [Node()], 'q' + name, [model.mname])

class BJTModel(Model):
    # If npn is true makes an NPN model, else a PNP model
    def __init__(self, npn, **kwargs):
        modelType = 'NPN' if npn else 'PNP'
        Model.__init__(self, modelType, attrs=kwargs)

# JFETs
class JFET(Component):
    ''' Input is the drain node, gate node
    Output is the source node'''
    def __init__(self, model, name = ''):
        Component.__init__(self, [Node(), Node()], [Node()], 'j' + name, [model.mname])

class JFETModel(Model):
    # If njf is true makes an NJF model, else a PJF model
    def __init__(self, njf, **kwargs):
        modelType = 'NJF' if njf else 'PJF'
        Model.__init__(self, modelType, attrs=kwargs)

# MOSFETs
class MOSFET(Component):
    ''' Input is the drain node, gate node
    Output is the source node, bulk node'''
    def __init__(self, model, name = ''):
        Component.__init__(self, [Node(), Node()], [Node(), Node()], 'm' + name, [model.mname])

class MOSFETModel(Model):
    # If nmos is true makes an NMOS model, else a PMOS model
    def __init__(self, nmos, **kwargs):
        modelType = 'NMOS' if nmos else 'PMOS'
        Model.__init__(self, modelType, attrs=kwargs)

# MESFETs
class MESFET(Component):
    ''' Input is the drain node, gate node
    Output is the source node'''
    def __init__(self, model, name = ''):
        Component.__init__(self, [Node(), Node()], [Node()], 'z' + name, [model.mname])

class MESFETModel(Model):
    # If nmf is true makes an NMF model, else a PMF model
    def __init__(self, nmf, **kwargs):
        modelType = 'NMF' if nmf else 'PMF'
        Model.__init__(self, modelType, attrs=kwargs)