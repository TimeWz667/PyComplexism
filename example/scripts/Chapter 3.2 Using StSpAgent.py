import complexism as cx
import epidag as dag


psc = """
    PCore pSIR {
        beta = 0.4
        gamma = 0.5
        Infect ~ exp(beta)
        Recov ~ exp(0.5)
        Die ~ exp(0.02)
    }
    """

dsc = """
CTBN SIR {
    life[Alive | Dead]
    sir[S | I | R]

    Alive{life:Alive}
    Dead{life:Dead}
    Inf{life:Alive, sir:I}
    Rec{life:Alive, sir:R}
    Sus{life:Alive, sir:S}

    Die -> Dead # from transition Die to state Dead by distribution Die
    Sus -- Infect -> Inf
    Inf -- Recov -> Rec

    Alive -- Die # from state Alive to transition Die
}
"""

bn = cx.read_pc(psc)
sm = dag.as_simulation_core(bn,
                            hie={'city': ['agent'],
                                 'agent': ['Recov', 'Die', 'Infect']})

pc = sm.generate()

dc = cx.read_dc(dsc)

Name = 'M1'
Gene = pc
proto = pc.breed('proto_agent_{}'.format('M1'), 'agent')
SIR = dc.generate_model(Name, **pc.get_child_actors('agent'))


def step(agent):
    evt = agent.Next
    agent.execute_event()
    agent.drop_next()
    agent.update_time(evt.Time)
    return evt.Time


if __name__ == '__main__':
    ag = cx.StSpAgent('Helen', SIR['Sus'])
    ag.initialise(0)

    print('Agent is a {}'.format(ag.State))
    ti = 0
    while ti < 100:
        ti = step(ag)
        print('Time:', ti)

        print('Agent is a {}'.format(ag.State))