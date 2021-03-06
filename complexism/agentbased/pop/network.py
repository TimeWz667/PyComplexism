import networkx as nx
from numpy.random import random, choice, shuffle
from epidag.factory import get_workshop
import epidag.factory.arguments as vld
from abc import ABCMeta, abstractmethod

__author__ = 'TimeWizard'
__all__ = ['INetwork', 'NetworkLibrary', 'NetworkSet',
           'NetworkGNP', 'NetworkBA', 'NetworkProb']


class INetwork(metaclass=ABCMeta):
    def __init__(self):
        self.Name = 'Network'
        self.json = None

    @abstractmethod
    def initialise(self):
        pass

    @abstractmethod
    def add_agent(self, ag):
        pass

    @abstractmethod
    def remove_agent(self, ag):
        pass

    @abstractmethod
    def reform(self):
        pass

    @abstractmethod
    def degree(self, ag):
        pass

    @abstractmethod
    def cluster(self, ag):
        pass

    @abstractmethod
    def match(self, net_src, ags_new):
        pass

    @abstractmethod
    def to_json(self):
        return self.json


class Network(INetwork, metaclass=ABCMeta):
    def __init__(self):
        INetwork.__init__(self)
        self.Graph = nx.Graph()

    def __getitem__(self, ag):
        try:
            return list(self.Graph[ag].keys())
        except KeyError:
            return list()

    def initialise(self):
        pass

    def add_agent(self, ag):
        self.Graph.add_node(ag)

    def remove_agent(self, ag):
        self.Graph.remove_node(ag)

    def degree(self, ag):
        return self.Graph.degree(ag)

    def cluster(self, ag):
        return nx.clustering(self.Graph, ag)

    def match(self, net_src, ags_new):
        for f, t in net_src.Graph.edges():
            self.Graph.add_edge(ags_new[f.Name], ags_new[t.Name])


class NetworkGNP(Network):
    def __init__(self, p):
        Network.__init__(self)
        self.P = p

    def add_agent(self, ag):
        self.Graph.add_node(ag)
        for ne in self.Graph.nodes():
            if ne is not ag and random() < self.P:
                self.Graph.add_edge(ag, ne)

    def reform(self):
        new = nx.Graph()
        new.add_nodes_from(self.Graph.node)
        g = nx.gnp_random_graph(len(self.Graph), self.P, directed=False)

        idmap = {i: ag for i, ag in enumerate(new.nodes.data().keys())}
        for u, v in g.edges():
            new.add_edge(idmap[u], idmap[v])
        self.Graph = new

    def __repr__(self):
        return 'GNP(N={}, P={})'.format(len(self.Graph), self.P)

    __str__ = __repr__

    def to_json(self):
        return {'Name': self.Name, 'Type': 'GNP', 'p': self.P}


class NetworkProb(INetwork):
    def __init__(self, p):
        INetwork.__init__(self)
        self.Outside = list()
        self.Inside = list()
        self.P = p

    def __getitem__(self, ag):
        if ag in self.Inside:
            return [nei for nei in self.Inside if ag is not nei]
        return []

    def add_agent(self, ag):
        if random() < self.P:
            self.Inside.append(ag)
        else:
            self.Outside.append(ag)

    def cluster(self, ag):
        # todo
        return 0

    def degree(self, ag):
        if ag in self.Outside:
            return 0
        else:
            return len(self.Inside) - 1

    def initialise(self):
        self.Outside = list()
        self.Inside = list()

    def match(self, net_src, ags_new):
        self.Outside = [ags_new[ag.Name] for ag in net_src.Outside]
        self.Inside = [ags_new[ag.Name] for ag in net_src.Inside]

    def remove_agent(self, ag):
        self.Outside.remove(ag)
        self.Inside.remove(ag)

    def reform(self):
        ags = list(self.Outside) + list(self.Inside)
        for ag in ags:
            self.add_agent(ag)

    def __repr__(self):
        n = len(self.Inside) + len(self.Outside)
        return 'Prob(N={}, P={})'.format(n, self.P)

    __str__ = __repr__

    def to_json(self):
        return {'Name': self.Name, 'Type': 'Prob', 'p': self.P}


class NetworkBA(Network):
    def __init__(self, m):
        Network.__init__(self)
        self.M = m
        self.__repeat = list()

    def add_agent(self, ag):
        """
        Add an agent into this network; adopted from barabasi_albert_graph in Networkx package
        :param ag: an agent in the model
        :type ag: Agent
        """

        self.Graph.add_node(ag)
        num = len(self.Graph)
        if num < self.M:
            self.__repeat.append(ag)
            return
        elif num is self.M:
            agl = [ag] * int(self.M)
            self.Graph.add_edges_from(zip(agl, self.__repeat))
            self.__repeat.extend(agl)
            return

        targets = set()
        while len(targets) < self.M:
            targets.add(choice(self.__repeat))
        agl = [ag] * self.M
        self.Graph.add_edges_from(zip(agl, targets))
        self.__repeat.extend(agl)

    def remove_agent(self, ag):
        self.__repeat = [a for a in self.__repeat if a is not ag]
        Network.remove_agent(self, ag)

    def reform(self):
        new = nx.Graph()
        new.add_nodes_from(self.Graph.node)
        g = nx.barabasi_albert_graph(len(self.Graph), self.M)
        ids = list(new.node.keys())
        shuffle(ids)
        idmap = {i: ag for i, ag in enumerate(ids)}
        for u, v in g.edges():
            new.add_edge(idmap[u], idmap[v])
        self.Graph = new

    def match(self, net_src, ags_new):
        Network.match(self, net_src, ags_new)
        self.__repeat = [ags_new[a.Name] for a in net_src.__repeat]

    def __repr__(self):
        return 'Barabasi_Albert(N={}, M={})'.format(len(self.Graph), self.M)

    __str__ = __repr__

    def to_json(self):
        return {'Name': self.Name, 'Type': 'BA', 'm': self.M}


class NetworkSet:
    def __init__(self):
        self.Nets = dict()

    def __setitem__(self, key, value):
        if not isinstance(value, INetwork):
            raise AttributeError('Network object should inherit from INetwork')
        self.Nets[key] = value

    def __getitem__(self, item):
        return self.Nets[item]

    def __contains__(self, item):
        return item in self.Nets

    def list(self):
        return list(self.Nets.keys())

    def append(self, net_name, net):
        if not isinstance(net, INetwork):
            raise AttributeError('Network object should inherit from INetwork')
        self.Nets[net_name] = net

    def append_from_json(self, net_name, js):
        net = NetworkLibrary.create_from_json(js)
        self.append(net_name, net)

    def append_from_def(self, net_name, df, loc=None):
        net = NetworkLibrary.parse(df, loc=loc)
        self.append(net_name, net)

    def reform(self, net=None):
        if net:
            try:
                self.Nets[net].reform()
            except KeyError:
                raise KeyError('No this net')
        else:
            for net in self.Nets.values():
                net.reform()

    def add_agent(self, ag):
        for net in self.Nets.values():
            net.add_agent(ag)

    def remove_agent(self, ag):
        for net in self.Nets.values():
            net.remove_agent(ag)

    def neighbours_of(self, ag, net=None):
        if net:
            try:
                return list(self.Nets[net][ag])
            except KeyError:
                return list()
        else:
            return {k: list(v[ag]) for k, v in self.Nets.items()}

    def neighbour_set_of(self, ag):
        ns = set()
        for net in self.Nets.values():
            try:
                ns.update(net[ag])
            except KeyError:
                pass
        return ns

    def clear(self, net=None):
        if net:
            try:
                self.Nets[net].clear()
            except KeyError:
                pass
        else:
            for net in self.Nets.values():
                net.clear()

    def match(self, nets_src, ags_new):
        for k, net_src in nets_src.Nets.items():
            self[k].match(net_src, ags_new)

    def __repr__(self):
        return '[{}]'.format(', '.join(['{}: {}'.format(*it) for it in self.Nets.items()]))

    def __str__(self):
        return '[{}]'.format('\n'.join(['\t{}: {}'.format(*it) for it in self.Nets.items()]))


NetworkLibrary = get_workshop('Networks')
NetworkLibrary.register('BA', NetworkBA, [vld.PositiveInteger('m')], ['name'])
NetworkLibrary.register('GNP', NetworkGNP, [vld.Prob('p')], ['name'])
NetworkLibrary.register('Category', NetworkProb, [vld.Prob('p')], ['name'])


if __name__ == '__main__':
    ns1 = NetworkBA(m=2)
    ns2 = NetworkGNP(p=0.3)
    ns3 = NetworkProb(p=0.2)

    for nod in range(20):
        ns1.add_agent('Ag{}'.format(nod))
        ns2.add_agent('Ag{}'.format(nod))
        ns3.add_agent('Ag{}'.format(nod))

    # ns1.reform()
    ag1 = ns1['Ag1']
    nsc = NetworkSet()
    nsc['N1'] = NetworkBA(m=2)
    nsc['N2'] = NetworkGNP(p=0.3)

    for nod in range(100):
        nsc.add_agent('Ag{}'.format(nod))

    print(nsc.neighbours_of('Ag1'))
    print(nsc.neighbours_of('Ag2', 'N1'))
