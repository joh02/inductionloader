# -*- coding: utf-8 -*-

import time

from logger import writeLogMsg

##############################################################################
class State():
    ''' Ablaufsteuerung des Lade-/Entlade-/Messzyklus
        -gewartet wird jeweils auf/vor Betreten, Aktivsein des states
        (condition/Weiterschaltbedingung)
    '''

    def __init__(self, name, condition, paramWSB, action, paramAction, nextName, altNextName, log=False):
        '''

        :param name: Name des states
        :param condition: Funktion die nach Erreichen einer Weiterschaltbedingung True liefert
        :param paramWSB: ihre Parameter
        :param action: Funktion die die eignetlichen Aktionen des states ausführt
        :param paramAction: ihre Parameter
        :param nextName: nächster state der eingenommen wird, wenn aktueller True liefert
        :param altNextName: nächster state der eingenommen wird, wenn aktueller False liefert
        :param log:
        '''
        self.name = name
        self.condition = condition
        self.paramWSB = paramWSB
        self.action = action
        self.paramAction = paramAction
        self.nextName = nextName
        self.altNextName = altNextName
        self.log = log


#--------------------------------------conditions------------------------------
def go():
    return True

#------------------------------------------------------------------------------
def wait_ms(ms):
    print(f'wait {ms}ms')
    time.sleep(ms/1000.)
    return True
#------------------------------------------------------------------------------
def wait_s(s):
    print(f'wait {s}sek.')
    time.sleep(s)
    return True

def wait_q():
    # wait_key() # funzte wohl nicht
    writeLogMsg('function wait_key called')
    return True

#--------------------------------------actions---------------------------------
def doNothing():
    '''
    dummy
    '''
    print('do nothing')
    return True

#------------------------------------------------------------------------------
def execute_state_chain(stateChain, startName):
    stateName = startName
    while stateName != "end":
        state = stateChain[stateName]
        if state.log:
            writeLogMsg(f'doing: {state.name}')
        else:
            print(f'doing: {state.name}')
        state.condition(*state.paramWSB)

        # wenn state.action() False zurückliefert dann altern. state setzen:
        retVal = state.action(*state.paramAction)
        if retVal:
            stateName = state.nextName
        else:
            stateName = state.altNextName