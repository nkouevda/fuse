# Tomer Kaftan, Nikita Kouevda, Daniel Wong
# 2013/05/12

from fuse.core import Component, Node, Model


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
    """Metal–oxide–semiconductor field-effect transistor.

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
