'''
BDD-style Lancelot specifications for the behaviour of the core library classes
'''

import lancelot, sys, types
from lancelot.comparators import Type, SameAs
from waferslim.execution import ExecutionContext, Results, Instructions, \
                                instruction_for
from waferslim.instructions import Make, Import, Call, CallAndAssign
from waferslim.specs.spec_classes import ClassWithNoArgs, ClassWithOneArg, \
                                         ClassWithTwoArgs

class ExecutionContextBehaviour(object):
    ''' Related Specs for ExecutionContext behaviour '''
    
    @lancelot.verifiable
    def get_builtin_type(self):
        ''' get_type() should return any requested builtin type '''
        spec = lancelot.Spec(ExecutionContext())
        spec.get_type('dict').should_be(dict)
        spec.get_type('str').should_be(str)

    @lancelot.verifiable
    def get_imported_module(self):
        ''' get_module() should return a requested module. 
        The same module should be returned on successive invocations. 
        The same module should be returned from different contexts '''
        spec = lancelot.Spec(ExecutionContext())
        spec.get_module('waferslim').should_be(Type(types.ModuleType))
        spec.get_module('waferslim.specs').should_be(Type(types.ModuleType))
        
        same_context = ExecutionContext()
        for name in ('waferslim', 'waferslim.specs.spec_classes'):
            spec.get_module(name).should_be(sys.modules[name])
            module = same_context.get_module(name)
            spec = lancelot.Spec(same_context)
            spec.get_module(name).should_be(SameAs(module))
        
        different_context = ExecutionContext()
        module = different_context.get_module('waferslim.examples')
        spec = lancelot.Spec(ExecutionContext())
        spec.get_module('waferslim.examples').should_be(SameAs(module))

    @lancelot.verifiable
    def get_module_type(self):
        ''' get_type() should return a requested module type, given the fully
        qualified name including module. The same type should be returned on 
        successive invocations. The same type should be returned from
        different contexts. '''
        _types = {}
        _types['waferslim.specs.spec_classes.ClassWithNoArgs'] \
             = ClassWithNoArgs
        _types['waferslim.specs.spec_classes.ClassWithOneArg'] \
             = ClassWithOneArg
        _types['waferslim.specs.spec_classes.ClassWithTwoArgs'] \
             = ClassWithTwoArgs
        
        execution_context = ExecutionContext()
        spec = lancelot.Spec(execution_context)
        for name, _type in _types.items():
            spec.get_type(name).should_be(_type)
            
            same_type = execution_context.get_type(name)
            spec.get_type(name).should_be(SameAs(same_type))
            
            different_context_type = ExecutionContext().get_type(name)
            spec.get_type(name).should_be(SameAs(different_context_type))
            
    @lancelot.verifiable
    def raises_exceptions(self):
        ''' Requesting a non-existent module should raise ImportError.
        Requesting a non-existent type should raise TypeError.'''
        spec = lancelot.Spec(ExecutionContext())
        spec.get_module('none.such').should_raise(ImportError)
        spec.get_type('none.such.Type').should_raise(ImportError)
        spec.get_type('NoneSuchType').should_raise(TypeError)
        spec.get_type('waferslim.Mint').should_raise(TypeError)
            
    @lancelot.verifiable
    def stores_instance(self):
        ''' store_instance(name, value) should put the name,value pair in the
        instances dict where it can be retrieved by get_instance(name). 
        instances should be isolated across execution contexts'''
        spec = lancelot.Spec(ExecutionContext())
        spec.get_instance('wafer thin').should_raise(KeyError)

        spec.when(spec.store_instance('wafer thin', 'mint'))
        spec.then(spec.get_instance('wafer thin')).should_be('mint')

        spec = lancelot.Spec(ExecutionContext())
        spec.get_instance('wafer thin').should_raise(KeyError)

lancelot.grouping(ExecutionContextBehaviour)

@lancelot.verifiable
def instruction_for_behaviour():
    ''' instruction_for should return instantiate the correct type of 
    instruction, based on the name given in the list passed to it ''' 
    spec = lancelot.Spec(instruction_for)
    known_instructions = {'make':Type(Make),
                          'import':Type(Import),
                          'call':Type(Call),
                          'callAndAssign':Type(CallAndAssign)}
    for name, instruction in known_instructions.items():
        spec.instruction_for(['id', name, []]).should_be(instruction)

@lancelot.verifiable
def instructions_behaviour():
    ''' Instructions should collaborate with instruction_for to instantiate
    a list of instructions, which execute() loops through '''
    mock_fn = lancelot.MockSpec(name='mock_fn')
    mock_make = lancelot.MockSpec(name='mock_make')
    mock_call = lancelot.MockSpec(name='mock_call')
    a_list = [
              ['id_0', 'make', 'instance', 'fixture', 'argument'],
              ['id_1', 'call', 'instance', 'f', '3']
             ]
    instructions = Instructions(a_list, 
                                lambda item: mock_fn.instruction_for(item))
    spec = lancelot.Spec(instructions)
    ctx = ExecutionContext()
    results = Results() 
    spec.execute(ctx, results).should_collaborate_with(
            mock_fn.instruction_for(a_list[0]).will_return(mock_make),
            mock_make.execute(ctx, results),
            mock_fn.instruction_for(a_list[1]).will_return(mock_call),
            mock_call.execute(ctx, results)
        )

class ResultsBehaviour(object):
    ''' Group of related specs for Results behaviour '''
    
    @lancelot.verifiable
    def completed_ok(self):
        ''' completed_ok() should add to results list. 
        Results list should be accessible through collection() '''
        instruction = lancelot.MockSpec(name='instruction')
        spec = lancelot.Spec(Results())
        spec.completed(instruction).should_collaborate_with(
            instruction.instruction_id().will_return('a')
            )
        spec.collection().should_be([['a', 'OK']])

    @lancelot.verifiable
    def raised(self):
        ''' raised() should add a translated error message to results list. 
        Results list should be accessible through collection() '''
        formatted_cause = '__EXCEPTION__: message:<<bucket>>'
        instruction = lancelot.MockSpec(name='instruction')
        spec = lancelot.Spec(Results())
        spec.failed(instruction, 'bucket')
        spec.should_collaborate_with(
            instruction.instruction_id().will_return('b')
            )
        spec.collection().should_be([['b', formatted_cause]])
        
    @lancelot.verifiable
    def completed_with_result(self):
        ''' completed() should add to results list. 
        Results list should be accessible through collection() '''
        instruction = lancelot.MockSpec(name='instruction')
        result = lancelot.MockSpec(name='result')
        spec = lancelot.Spec(Results())
        spec.completed(instruction, result=result).should_collaborate_with(
            instruction.instruction_id().will_return('b')
            )
        spec.collection().should_be([['b', str(result)]])
        
    @lancelot.verifiable
    def completed_without_return_value(self):
        ''' completed() should add to results list. 
        Results list should be accessible through collection() '''
        instruction = lancelot.MockSpec(name='instruction')
        spec = lancelot.Spec(Results())
        spec.completed(instruction, result=None).should_collaborate_with(
            instruction.instruction_id().will_return('c')
            )
        spec.collection().should_be([['c', '/__VOID__/']])

lancelot.grouping(ResultsBehaviour)

if __name__ == '__main__':
    lancelot.verify()