''' This module has state, demonstrating that each ExecutionContext
has its own isolated copy of the module each with its own state '''

state = []

class StateAlteringClass(object):
    ''' Simple class that alters the module state '''
    def alter_state(self):
        ''' Alter the module state '''
        state.append(len(state)+1)
    def get_state(self):
        ''' return the module state '''
        return state