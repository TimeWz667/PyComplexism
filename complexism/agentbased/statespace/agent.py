from complexism.element import Event
from complexism.agentbased import GenericAgent, GenericBreeder
from .modifier import ModifierSet


__author__ = 'TimeWz667'
__all__ = ['StSpAgent', 'StSpBreeder']


class StSpAgent(GenericAgent):
    def __init__(self, name, st, pars=None):
        GenericAgent.__init__(self, name, pars)
        self.State = st
        self.Transitions = dict()
        self.Modifiers = ModifierSet()

    def __getitem__(self, item):
        try:
            return GenericAgent.__getitem__(self, item)
        except KeyError as e:
            if item == 'State':
                return self.State
            else:
                raise e

    def initialise(self, time=0, **kwargs):
        self.Transitions.clear()
        self.update_time(time)

    def reset(self, time=0, *args, **kwargs):
        self.Transitions.clear()
        self.update_time(time)

    def find_next(self):
        if self.Transitions:
            return Event(*min(self.Transitions.items(), key=lambda x: x[1]))
        else:
            return Event.NullEvent

    def execute_event(self):
        nxt = self.Next
        if nxt is not Event.NullEvent:
            self.State = self.State.execute(nxt)

    def update_time(self, time):
        new_trs = self.State.next_transitions()
        ad = list(set(new_trs) - set(self.Transitions.keys()))
        self.Transitions = {k: v for k, v in self.Transitions.items() if k in new_trs}
        for tr in ad:
            tte = tr.rand(self)
            for mo in self.Modifiers.on(tr):
                tte = mo.modify(tte)
            self.Transitions[tr] = tte + time
        self.drop_next()

    def add_modifier(self, mod):
        """
        Append a modifier
        :param mod:
        :type mod: Modifier
        """
        self.Modifiers[mod.Name] = mod

    def shock(self, time, source, target, value):
        """
        Make an impulse on a modifier
        :param time: time
        :type time: float
        :param source: source of impulse, None for state space model
        :type source: str
        :param target: target modifier
        :type target: str
        :param value: value of impulse
        """
        mod = self.Modifiers[target]
        if mod.update(value):
            self.modify(target, time)

    def modify(self, m, time):
        """
        Re-modify a transition via modifier m
        :param m: target modifier
        :type m: str
        :param time: time
        :type time: float
        """
        mod = self.Modifiers[m]
        if mod.target in self.Transitions:
            tr = mod.target
            tte = tr.rand()
            for mo in self.Modifiers.on(tr):
                tte = mo.modify(tte)
            self.Transitions[tr] = tte + time
            self.drop_next()

    def isa(self, st):
        return st in self

    def __contains__(self, st):
        return st in self.State

    def clone(self, dc_new=None):
        if dc_new:
            ag_new = StSpAgent(self.Name, dc_new[self.State.Name])
            for tr, tte in self.Transitions.items():
                ag_new.Transitions[dc_new.Transitions[tr.Name]] = tte
        else:
            ag_new = StSpAgent(self.Name, self.State)

        ag_new.Attributes.update(self.Attributes)
        return ag_new

    def to_json(self):
        js = GenericAgent.to_json(self)
        js['State'] = self.State.Name
        js['Transitions'] = {tr.Name: tte for tr, tte in self.Transitions.items()}
        js['Modifiers'] = self.Modifiers.to_json()
        return js

    def to_snapshot(self):
        js = GenericAgent.to_json(self)
        js['State'] = self.State.Name
        return js

    def to_data(self):
        dat = GenericAgent.to_data(self)
        dat['State'] = self.State.Name
        return dat


class StSpBreeder(GenericBreeder):
    def __init__(self, name, group, pc_parent, dc, **kwargs):
        GenericBreeder.__init__(self, name=name, group=group, pc_parent=pc_parent, **kwargs)
        self.DCore = dc.generate_model(name, **self.PCore.get_samplers())
        self.WStates = {wd: self.DCore[wd] for wd in self.DCore.WellDefinedStates}

    def _filter_attributes(self, kw):
        sts = {'st': self.WStates[kw['st']]}
        del kw['st']
        return sts, kw

    def _new_agent(self, name, pars, **kwargs):
        return StSpAgent(name, kwargs['st'], pars=pars)

    def count(self, ags, **kwargs):
        try:
            st = kwargs['st']
        except KeyError:
            return len(ags)

        try:
            st = self.DCore[st]
            return sum(st in ag for ag in ags)
        except KeyError:
            return 0