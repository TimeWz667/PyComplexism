from abc import ABCMeta, abstractmethod
from complexism.element import Event, Schedule
from complexism.mcore import ModelSelector


class AbsModel(metaclass=ABCMeta):
    def __init__(self, name, env=None):
        self.Name = name
        self.Scheduler = Schedule(self.Name)
        self.Validator = None
        self.Environment = env

    @abstractmethod
    def collect_requests(self):
        pass

    @abstractmethod
    def find_next(self):
        pass

    def request(self, event, who):
        self.Scheduler.append_request_from_source(event, who)

    @abstractmethod
    def do_request(self, req):
        pass

    @property
    def Next(self):
        if self.Scheduler.is_empty():
            self.find_next()
        return self.Scheduler

    @property
    def TTE(self):
        return self.Scheduler.Time

    @abstractmethod
    def validate_requests(self):
        pass

    @abstractmethod
    def fetch_requests(self, rs):
        pass

    @abstractmethod
    def execute_requests(self):
        pass

    def disclose(self, msg, who):
        self.Scheduler.append_disclosure_from_source(msg, who)

    @abstractmethod
    def collect_disclosure(self):
        pass

    @abstractmethod
    def impulse_externally(self, dss, ti):
        pass

    def exit_cycle(self):
        self.Scheduler.cycle_completed()

    @abstractmethod
    def print_schedule(self):
        pass


class LeafModel(AbsModel, metaclass=ABCMeta):
    def __init__(self, name, env):
        AbsModel.__init__(self, name, env)

    def collect_requests(self):
        self.find_next()
        self.Scheduler.collection_completed()

    def validate_messages(self):
        # todo validation if not validated, disapprove
        pass

    def fetch_requests(self, rs):
        self.Scheduler.fetch_requests(rs)
        self.Scheduler.validation_completed()

    def execute_requests(self):
        if self.Scheduler.waiting_for_execution():
            for req in self.Scheduler.Requests:
                self.do_request(req)
            self.Scheduler.execution_completed()

    def print_schedule(self):
        self.Scheduler.print()


class BranchModel(AbsModel, metaclass=ABCMeta):
    def __init__(self, name, env=None):
        AbsModel.__init__(self, name, env)

    @abstractmethod
    def all_models(self)->dict:
        pass

    @abstractmethod
    def get_model(self, k):
        pass

    def select(self, mod):
        return self.get_model(mod)

    def select_all(self, sel):
        return ModelSelector(self.all_models()).select_all(sel)

    def collect_messages(self):
        self.find_next()
        for v in self.all_models().values():
            v.collect_messages()
            self.Scheduler.append_lower_schedule(v.Scheduler)
        self.Scheduler.collection_completed()

    def validate_messages(self):
        pass  # todo

    def fetch_requests(self, rs):
        self.Scheduler.fetch_requests(rs)

        res = self.Scheduler.pop_lower_requests()

        for k, v in res.items():
            self.select(k).fetch_requests(v)
        self.Scheduler.validation_completed()

    def execute_requests(self):
        if self.Scheduler.waiting_for_execution():
            for req in self.Scheduler.Requests:
                self.do_request(req)
            self.Scheduler.execution_completed()

        for v in self.all_models().values():
            v.execute_requests()

    @abstractmethod
    def do_request(self, req):
        pass

    def print_schedule(self):
        self.Scheduler.print()
        print()
        for m in self.all_models().values():
            m.print_schedule()


class Country(BranchModel):
    def __init__(self, name):
        BranchModel.__init__(self, name)
        self.Models = dict()
        self.Check = False

    def all_models(self) -> dict:
        return self.Models

    def get_model(self, k):
        return self.Models[k]

    def do_request(self, req):
        self.disclose(req.Message, req.When)
        print(req)

    def find_next(self):
        if not self.Check:
            self.request(Event('Country', 5), 'self')

    def impulse_externally(self, dss, ti):
        pass


class City(BranchModel):
    def __init__(self, name):
        BranchModel.__init__(self, name)
        self.Models = dict()
        self.Check = False

    def all_models(self) -> dict:
        return self.Models

    def get_model(self, k):
        return self.Models[k]

    def do_request(self, req):
        self.disclose(req.Message, req.When)

    def find_next(self):
        if not self.Check:
            self.request(Event('City', 3), 'self')

    def impulse_externally(self, dss, ti):
        pass


from numpy.random import random


class School(LeafModel):
    def __init__(self, name):
        LeafModel.__init__(self, name, None)
        self.Last = 0

    def find_next(self):
        self.request(Event(self.Name, self.Last+abs(random())), 'student')

    def do_request(self, req):
        self.disclose(req.When, self.Name)
        self.Last = req.When

    def impulse_externally(self, dss, ti):
        pass


tw = Country('Taiwan')
tp = City('Taipei')
tw.Models['Taipei'] = tp

tn = City('Tainan')
tw.Models['Tainan'] = tn

for st in range(2):
    n = 'S{}'.format(st)
    tp.Models[n] = School(n)

for st in range(2):
    n = 'S{}'.format(st)
    tn.Models[n] = School(n)

# tw.print_schedule()
tw.collect_messages()
#print('\nCollecting Requests\n')
# tw.print_schedule()

# print('\nValidating Requests\n')
req = tw.Scheduler.Requests
print(req)
tw.fetch_requests(req)
# tw.print_schedule()

# print('\nExecute Requests\n')
tw.execute_requests()
tw.print_schedule()

tw.collect_messages()
req = tw.Scheduler.Requests
tw.fetch_requests(req)
tw.execute_requests()
tw.print_schedule()
print(req)
