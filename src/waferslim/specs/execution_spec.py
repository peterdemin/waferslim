'''
BDD-style Lancelot specifications for the behaviour of the core library classes
'''

import lancelot, logging, os, sys, types
from lancelot.comparators import Type, SameAs
from waferslim.execution import ExecutionContext, Results, Instructions, \
                                instruction_for, ParamsConverter
from waferslim.instructions import Make, Import, Call, CallAndAssign, \
                                   Instruction

class ExecutionContextBehaviour(object):
    ''' Related Specs for ExecutionContext behaviour '''
    
    def _nonsrc_path(self, execution_context):
        ''' Path to non-src modules that are known to be outside sys.path '''
        slim_path = execution_context.get_module('waferslim').__path__[0]
        path = os.path.abspath(slim_path 
                               + '%s..%snon-waferslim' % (os.sep, os.sep))
        return path

    @lancelot.verifiable
    def uses_added_import_paths(self):
        ''' add_import_path() should allow packages or modules to be found 
        without altering sys.path'''
        execution_context = ExecutionContext()
        spec = lancelot.Spec(execution_context)
        spec.get_module('import_me').should_raise(ImportError)
        
        path = self._nonsrc_path(execution_context)
        spec.when(spec.add_import_path(path))
        spec.then(spec.get_module('import_me')).should_not_raise(ImportError)
        
        lancelot.Spec(sys.path).it().should_not_contain(path)
        
    @lancelot.verifiable
    def get_imported_module(self):
        ''' get_module() should return a requested module, which should not
        then exist in sys.modules if it has been dynamically loaded.
        The same module should be returned on successive invocations. 
        The same module should not be returned from different contexts '''
        
        same_context = ExecutionContext()
        same_context.add_import_path(self._nonsrc_path(same_context))
        different_context = ExecutionContext()
        different_context.add_import_path(self._nonsrc_path(different_context))
        for name in ('import_me', 
                     'module_with_state'):
            spec = lancelot.Spec(same_context)
            spec.get_module(name).should_be(Type(types.ModuleType))

            same_module = same_context.get_module(name)
            spec.get_module(name).should_be(SameAs(same_module))
            
            sys_spec = lancelot.Spec(sys.modules)
            sys_spec.it().should_not_contain(name)
        
            different_module = different_context.get_module(name)
            spec.get_module(name).should_not_be(SameAs(different_module))

    @lancelot.verifiable
    def get_module_type(self):
        ''' get_type() should return a requested module type, given the fully
        qualified name including module. The same type should be returned on 
        successive invocations. The same type should not be returned from
        different contexts. State in a module should be isolated within 
        each context'''
        _types = {'StateAlteringClass':'module_with_state'}
        
        execution_context = ExecutionContext()
        execution_context.add_import_path(self._nonsrc_path(execution_context))
        for name, _type in _types.items():
            fully_qualified_name = '%s.%s' % (_type, name) 
            same_type = execution_context.get_type(fully_qualified_name)

            lancelot.Spec(same_type.__name__).it().should_be(name)

            spec = lancelot.Spec(execution_context)
            spec.get_type(fully_qualified_name).should_be(SameAs(same_type))
            
            other_context = ExecutionContext()
            other_context.add_import_path(self._nonsrc_path(other_context))
            different_type = other_context.get_type(fully_qualified_name)
            spec.get_type(fully_qualified_name).should_not_be(
                                                SameAs(different_type))
            
            instances = same_type(), different_type()
            spec = lancelot.Spec(instances[0])
            spec.when(spec.alter_state())
            spec.then(spec.get_state()).should_contain(1)
            spec.then(instances[1].get_state).should_not_contain(1)

    @lancelot.verifiable
    def handles_builtins(self):
        ''' get_type() should handle builtin types and get_module() should
        not affect sys.modules when module was already loaded, e.g. builtins'''
        spec = lancelot.Spec(ExecutionContext())
        spec.get_type('__builtin__.dict').should_be(dict)
        spec.get_type('__builtin__.str').should_be(str)
        spec.get_module('__builtin__').should_be(SameAs(sys.modules['__builtin__']))
    
    @lancelot.verifiable
    def raises_exceptions(self):
        ''' Requesting a non-existent module should raise ImportError.
        Requesting a non-existent type should raise TypeError.'''
        spec = lancelot.Spec(ExecutionContext())
        spec.get_module('no.such.module').should_raise(ImportError)
        spec.get_type('no.such.module.Type').should_raise(ImportError)
        spec.get_type('NoSuchType').should_raise(TypeError)
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

    @lancelot.verifiable
    def uses_added_type_context(self):
        ''' add_type_context() should allow classes to be found 
        without fully-dot-qualified prefixes'''
        ctx = ExecutionContext()
        spec = lancelot.Spec(ctx)
        spec.get_type('TestCase').should_raise(TypeError)
        
        spec.when(spec.add_type_prefix('unittest'))
        spec.then(spec.get_type('TestCase')).should_not_raise(TypeError)
        spec.then(spec.get_type('TestCase')).should_be(
            ctx.get_type('unittest.TestCase'))
        
    @lancelot.verifiable
    def stores_symbol(self):
        ''' store_symbol(name, value) should put the name,value pair in the
        symbols dict where it can be retrieved by get_symbol(name). 
        symbols should be isolated across execution contexts'''
        spec = lancelot.Spec(ExecutionContext())
        spec.get_symbol('another_bucket').should_raise(KeyError)

        spec.when(spec.store_symbol('another_bucket', 'for monsieur'))
        spec.then(spec.get_symbol('another_bucket')).should_be('for monsieur')

        spec = lancelot.Spec(ExecutionContext())
        spec.get_symbol('another_bucket').should_raise(KeyError)

lancelot.grouping(ExecutionContextBehaviour)

@lancelot.verifiable
def instruction_for_behaviour():
    ''' instruction_for should return / instantiate the correct type of 
    instruction, based on the name given in the list passed to it. If the name
    is not recognised the base Instruction class is returned. ''' 
    spec = lancelot.Spec(instruction_for)
    instructions = {'make':Type(Make),
                    'import':Type(Import),
                    'call':Type(Call),
                    'callAndAssign':Type(CallAndAssign),
                    'noSuchInstruction':Type(Instruction)}
    for name, instruction in instructions.items():
        spec.instruction_for(['id', name, []]).should_be(instruction)

class InstructionsBehaviour(object):
    ''' Group of Instructions-related specifications '''

    @lancelot.verifiable
    def loops_through_list(self):
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

    @lancelot.verifiable
    def handles_execute_exceptions(self):
        ''' execute() should catch thrown exceptions and register the 
        instruction as failed '''
        mock_fn = lancelot.MockSpec(name='mock_fn')
        mock_call = lancelot.MockSpec(name='mock_call')
        results = lancelot.MockSpec(name='results')
        a_list = [
                  ['id_', 'call', 'instance', 'fn', 'arg']
                 ]
        instructions = Instructions(a_list, 
                                    lambda item: mock_fn.instruction_for(item))
        spec = lancelot.Spec(instructions)
        ctx = ExecutionContext()
        msg = "I couldn't eat another thing. I'm absolutely stuffed."
        
        # Suppress warning log message that we know will be generated
        logger = logging.getLogger('Instructions')
        log_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)
        try:
            spec.execute(ctx, results).should_collaborate_with(
                mock_fn.instruction_for(a_list[0]).will_return(mock_call),
                mock_call.execute(ctx, results).will_raise(Exception(msg)),
                results.failed(mock_call, msg)
            )
        finally:
            # Put logger back to how it was
            logger.setLevel(log_level)

lancelot.grouping(InstructionsBehaviour)

class ResultsBehaviour(object):
    ''' Group of related specs for Results behaviour '''
    
    @lancelot.verifiable
    def completed_ok(self):
        ''' completed() for Make should add ok to results list. 
        Results list should be accessible through collection() '''
        instruction = lancelot.MockSpec(name='instruction')
        spec = lancelot.Spec(Results())
        spec.completed(instruction).should_collaborate_with(
            instruction.instruction_id().will_return('a')
            )
        spec.collection().should_be([['a', 'OK']])

    @lancelot.verifiable
    def failed(self):
        ''' failed() should add a translated error message to results list. 
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
        ''' completed() for Call should add to results list. 
        Results list should be accessible through collection() '''
        class Fake(object):
            def __str__(self):
                return 'Bon appetit'
        instruction = lancelot.MockSpec(name='instruction')
        spec = lancelot.Spec(Results())
        spec.completed(instruction, result=Fake()).should_collaborate_with(
            instruction.instruction_id().will_return('b'),
            )
        spec.collection().should_be([['b', 'Bon appetit']])
        
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

@lancelot.verifiable
def params_converter_behaviour():
    ''' ParamsConverter should create (possibly nested) tuple of string args
    from a (possibly nested) list of strings (possibly symbols) ''' 
    execution_context = lancelot.MockSpec('execution_context')
    spec = lancelot.Spec(ParamsConverter(execution_context))
    spec.to_args([], 0).should_be(())

    execution_context = lancelot.MockSpec('execution_context')
    spec = lancelot.Spec(ParamsConverter(execution_context))
    spec.to_args(['mint'], 0).should_be(('mint',))

    execution_context = lancelot.MockSpec('execution_context')
    spec = lancelot.Spec(ParamsConverter(execution_context))
    spec.to_args(['wafer', 'thin'], 0).should_be(('wafer', 'thin'))

    execution_context = lancelot.MockSpec('execution_context')
    spec = lancelot.Spec(ParamsConverter(execution_context))
    spec.to_args(['wafer', 'thin'], 1).should_be(('thin', ))

    execution_context = lancelot.MockSpec('execution_context')
    spec = lancelot.Spec(ParamsConverter(execution_context))
    spec.to_args(['$A', '$b_', 'C$'], 0).should_collaborate_with(
        execution_context.get_symbol('A').will_return('X'),
        execution_context.get_symbol('b_').will_return('Y'),
        and_result=(('X', 'Y', 'C$'))
        )
    
    execution_context = lancelot.MockSpec('execution_context')
    spec = lancelot.Spec(ParamsConverter(execution_context))
    spec.to_args([['bring', 'me'], ['another', 'bucket']], 0).should_be(
                 (('bring', 'me'), ('another', 'bucket'))
                )

if __name__ == '__main__':
    lancelot.verify()