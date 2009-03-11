''' This module has state, demonstrating that each ExecutionContext
has its own isolated copy of the module each with its own state '''

STATE = []

class StateAlteringClass(object):
    ''' Simple class that alters the module state '''
    def alter_state(self):
        ''' Alter the module state '''
        STATE.append(len(STATE)+1)
    def get_state(self):
        ''' return the module state '''
        return STATE