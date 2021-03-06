from json import JSONDecodeError
import logging
import epidag as dag
from complexism.fn import *

__author__ = 'TimeWz667'
__all__ = ['Director']


class Director:
    def __init__(self):
        self.BayesianNetworks = dict()
        self.StSpBlueprints = dict()
        self.SimModelBlueprints = dict()
        self.Log = logging.getLogger(__name__)

    def _add_bn(self, bn):
        if bn in self.BayesianNetworks:
            self.Log.warning('Bayesian Network {} have already existed'.format(bn.Name))
        else:
            self.BayesianNetworks[bn.Name] = bn
            self.Log.info('Bayesian Network {} added'.format(bn.Name))

    def _add_dbp(self, dbp):
        if dbp in self.StSpBlueprints:
            self.Log.warning('State-Space Model {} have already existed'.format(dbp.Name))
        else:
            self.StSpBlueprints[dbp.Name] = dbp
            self.Log.info('State-Space Model {} added'.format(dbp.Name))

    def _add_mbp(self, mbp):
        if mbp in self.SimModelBlueprints:
            self.Log.warning('Simulation Model {} have already existed'.format(mbp.Class))
        else:
            self.SimModelBlueprints[mbp.Class] = mbp
            self.Log.info('Simulation Model {} added'.format(mbp.Class))

    def get_bayes_net(self, bn_name):
        try:
            return self.BayesianNetworks[bn_name]
        except KeyError:
            self.Log.warning('Unknown BayesNet')

    def get_state_space_model(self, ss_name):
        try:
            return self.StSpBlueprints[ss_name]
        except KeyError:
            self.Log.warning('Unknown State-Space Model')

    def get_sim_model(self, sm_name):
        try:
            return self.SimModelBlueprints[sm_name]
        except KeyError:
            self.Log.warning('Unknown Simulation Model')

    def has_bayes_net(self, bn_name):
        """
        Check if the director has the Bayesian Network
        :param bn_name: name of the Bayesian Network
        :return: has or not
        :rtype: bool
        """
        return bn_name in self.BayesianNetworks

    def has_state_space_model(self, ss_name):
        """
        Check if the director has the state space model
        :param ss_name: name of the state space model
        :return: has or not
        :rtype: bool
        """
        return ss_name in self.StSpBlueprints

    def has_sim_model(self, sm_name):
        """
        Check if the director has the simulation model
        :param sm_name: name of the simulation model
        :return: has or not
        :rtype: bool
        """
        return sm_name in self.SimModelBlueprints

    def read_bayes_net(self, script):
        """
        Read a script of a Bayesian Network
        :param script: script of a Bayesian Network
        :type script: string
        """
        bn = read_bn_script(script)
        self._add_bn(bn)

    def load_bayes_net(self, file):
        """
        Load a js of a Bayesian Network
        :param file: json of a Bayesian Network
        :type file: dict or string
        """
        try:
            bn = read_bn_json(load_json(file))
        except JSONDecodeError:
            bn = read_bn_script(load_txt(file))
        self._add_bn(bn)

    def save_bayes_net(self, bn_name, file):
        try:
            bn = self.get_bayes_net(bn_name)
            save_bn(bn, file)
        except KeyError:
            self.Log.warning('BayesNet {} not found'.format(bn_name))

    def list_bayes_nets(self):
        return list(self.BayesianNetworks.keys())

    def read_state_space_model(self, script):
        bn = read_dbp_script(script)
        self._add_dbp(bn)

    def load_state_space_model(self, file):
        try:
            dbp = read_dbp_json(load_json(file))
        except JSONDecodeError:
            dbp = read_dbp_script(load_txt(file))
        self._add_dbp(dbp)

    def new_state_space_model(self, dbp_name, dc_type):
        """
        Generate a new blueprint of a state-space dynamic model
        :param dbp_name: name of the model
        :param dc_type: type of dynamic core, CTBN or CTMC
        :return: a new Blueprint
        """
        dbp = new_dbp(dbp_name, dc_type)
        self._add_dbp(dbp)
        return dbp

    def save_state_space_model(self, dbp_name, file):
        try:
            dbp = self.get_state_space_model(dbp_name)
            save_dbp(dbp, file)
        except KeyError:
            self.Log.warning('Unknown State-Space Model')

    def list_state_spaces(self):
        return list(self.StSpBlueprints.keys())

    def load_sim_model(self, file):
        # todo
        try:
            mbp = read_mbp_json(load_json(file))
        except JSONDecodeError:
            raise TypeError('Unknown format')
            #mbp = read_mbp_script(load_txt(file))
        self._add_mbp(mbp)

    def new_sim_model(self, mbp_name, model_type):
        """
        Generate a new blueprint of a dynamic core
        :param mbp_name: name of the model
        :param model_type: type of simulation model, StSpABM, SSODE, ODEEBM
        :return: a new Blueprint
        """
        mbp = new_mbp(mbp_name, model_type)
        self._add_mbp(mbp)
        return mbp

    def save_sim_model(self, sm_name, file):
        # todo
        try:
            mbp = self.get_sim_model(sm_name)
            save_mbp(mbp, file)
        except KeyError:
            self.Log.warning('Model Blueprint {} not found'.format(mbp_name))

    def list_sim_models(self):
        """
        List the names of all the simulation models
        :return: the names of all the simulation models
        :rtype: list
        """
        return list(self.SimModelBlueprints.keys())

    def save(self, file):
        js = dict()
        js['PCores'] = {k: v.to_json() for k, v in self.BayesianNetworks.items()}
        js['DCores'] = {k: v.to_json() for k, v in self.StSpBlueprints.items()}
        js['MCores'] = {k: v.to_json() for k, v in self.SimModelBlueprints.items()}
        save_json(js, file)

    def load(self, file):
        # todo
        js = load_json(file)
        self.BayesianNetworks.update({k: read_bn_json(v) for k, v in js['PCores'].items()})
        self.StSpBlueprints.update({k: read_dbp_json(v) for k, v in js['DCores'].items()})
        self.SimModelBlueprints.update({k: read_mbp_json(v) for k, v in js['MCores'].items()})
        # self.ModelLayouts.update({k: load_layout(v) for k, v in js['Layouts'].items()})

    def generate_model(self, name, sim_model, **kwargs):
        mbp = self.get_sim_model(sim_model)
        if 'bn' in kwargs:
            bn = kwargs['bn']
            del kwargs['bn']
            if isinstance(bn, str):
                bn = self.get_bayes_net(bn)
            hei = mbp.get_parameter_hierarchy(da=self)
            sm = dag.as_simulation_core(bn, hei)
            pc = sm.generate(name, **kwargs)
        elif 'pc' in kwargs:
            pc = kwargs['pc']
        else:
            self.Log.error('Undefined parameter information')
            return

        return mbp.generate(name, da=self, pc=pc)

    def get_y0_proto(self, sim_model):
        sm = self.get_sim_model(sim_model)
        return sm.get_y0s()

    def get_y0s(self, sim_model):
        sm = self.get_sim_model(sim_model)
        return sm.get_y0s(da=self)

    def copy_model(self, mod_src, **kwargs):
        cls_src = mod_src.Class
        if not cls_src or not (self.has_sim_model(cls_src) or self.has_model_layout(cls_src)):
            self.Log.warning("The prototype of the model cannot be identified")
            return None
        # todo

