'''
BDD-style Lancelot specifications for the behaviour of the core library classes
'''

import lancelot
from waferslim.execution import Instruction, InstructionException, \
                                Make, Import, Call, CallAndAssign

class BaseInstructionBehaviour(object):
    ''' Related Specs for base Instruction behaviour '''
    
    @lancelot.verifiable
    def params_must_be_list(self):
        ''' The params constructor arg must be a list '''
        new_instance_with_bad_parms = lambda: Instruction('id', 'params')
        spec = lancelot.Spec(new_instance_with_bad_parms)
        spec.__call__().should_raise(InstructionException)

        new_instance_with_list_parms = lambda: Instruction('id', ['params'])
        spec = lancelot.Spec(new_instance_with_list_parms)
        spec.__call__().should_not_raise(InstructionException)
        
    @lancelot.verifiable
    def id_and_params_stored(self):
        ''' The id and params constructor args should be assigned to fields '''
        class FakeInstruction(Instruction):
            ''' Fake Instruction to get fields from '''
            def execute(self):
                ''' Get the fields '''
                return [self._id, self._params]
        spec = lancelot.Spec(FakeInstruction('an_id', ['param1', 'param2']))
        spec.execute().should_be(['an_id', ('param1', 'param2')])

lancelot.grouping(BaseInstructionBehaviour)

if __name__ == '__main__':
    lancelot.verify()