'''
BDD-style Lancelot specifications for the behaviour of the core library classes
'''

import lancelot
from lancelot.comparators import Type
from waferslim.instructions import Instruction, \
                                   Make, Import, Call, CallAndAssign
from waferslim.specs.spec_classes import ClassWithNoArgs, ClassWithOneArg, \
                                         ClassWithTwoArgs

class BaseInstructionBehaviour(object):
    ''' Related Specs for base Instruction behaviour '''
    
    @lancelot.verifiable
    def params_must_be_list(self):
        ''' The params constructor arg must be a list '''
        new_instance_with_bad_parms = lambda: Instruction('id', 'params')
        spec = lancelot.Spec(new_instance_with_bad_parms)
        spec.__call__().should_raise(TypeError)

        new_instance_with_list_parms = lambda: Instruction('id', ['params'])
        spec = lancelot.Spec(new_instance_with_list_parms)
        spec.__call__().should_not_raise(Exception)
        
    @lancelot.verifiable
    def stores_id_and_params(self):
        ''' The id and params constructor args should be assigned to fields.
        The instruction id should be accessible through a method. '''
        class FakeInstruction(Instruction):
            ''' Fake Instruction to get fields from '''
            def execute(self, execution_context, results):
                ''' Get the fields '''
                return self._params
        spec = lancelot.Spec(FakeInstruction('an_id', ['param1', 'param2']))
        spec.instruction_id().should_be('an_id')
        spec.execute(object(), object()).should_be(['param1', 'param2'])
        
    @lancelot.verifiable
    def execute_fails(self):
        ''' The base class execute() method fails with INVALID_STATEMENT '''
        instruction = Instruction('id', ['nonsense'])
        spec = lancelot.Spec(instruction)
        execution_context = lancelot.MockSpec('execution_context')
        results = lancelot.MockSpec('results')
        spec.execute(execution_context, results).should_collaborate_with(
                results.failed(instruction, 'INVALID_STATEMENT nonsense')
            )
    
    @lancelot.verifiable
    def repr_should_be_meaningful(self):
        ''' repr(Instruction) should provide meaningful information'''
        instruction = Instruction('id', ['param1', 'param2'])
        spec = lancelot.Spec(instruction.__repr__)
        spec.__call__().should_be("Instruction id: ['param1', 'param2']")
        
lancelot.grouping(BaseInstructionBehaviour)

@lancelot.verifiable
def make_creates_instance():
    ''' Make.execute() should instantiate the class & add it to context '''
    package = 'waferslim.specs.spec_classes'
    
    # Case where no args are supplied
    make = Make('id', ['instance', '%s.%s' % (package, 'ClassWithNoArgs')])
    spec = lancelot.Spec(make)
    execution_context = lancelot.MockSpec(name='execution_context')
    results = lancelot.MockSpec(name='results')
    spec.execute(execution_context, results).should_not_raise(Exception)
    
    # Cases where args are supplied
    classes = {ClassWithNoArgs:[],
               ClassWithOneArg:[1],
               ClassWithTwoArgs:['a', 'b']}
    for target in classes.keys():
        name = target.__name__
        execution_context = lancelot.MockSpec(name='execution_context')
        results = lancelot.MockSpec(name='results')
        params = [name, '%s.%s' % (package, name), classes[target]]
        make_instruction = Make(name, params)
        spec = lancelot.Spec(make_instruction)
        spec.execute(execution_context, results).should_collaborate_with(
            execution_context.get_type(params[1]).will_return(target),
            execution_context.store_instance(name, Type(target)),
            results.completed(make_instruction)
        )

class MakeExceptionBehaviour(object):
    ''' Exception-related Specs for Make-instruction behaviour '''

    @lancelot.verifiable
    def handles_wrong_args(self):
        ''' NoSuchConstructorException indicates incorrect constructor args '''
        wrong_params = ['creosote', 'FakeClass',
                        ['some unwanted', 'constructor args']
                       ]
        cause = 'COULD_NOT_INVOKE_CONSTRUCTOR FakeClass ' \
                + 'default __new__ takes no parameters'
        execution_context = lancelot.MockSpec(name='execution_context')
        results = lancelot.MockSpec(name='results')
        a_class = ClassWithNoArgs
        make_instruction = Make('wrong params', wrong_params)
        spec = lancelot.Spec(make_instruction)
        spec.execute(execution_context, results).should_collaborate_with(
            execution_context.get_type('FakeClass').will_return(a_class),
            results.failed(make_instruction, cause)
        )

    @lancelot.verifiable
    def handles_bad_type(self):
        ''' NoSuchClassException indicates unknown type '''
        wrong_params = ['creosote', 'FakeClass',
                        ['some unwanted', 'constructor args']
                       ]
        type_error = TypeError('x')
        cause = 'NO_CLASS FakeClass x'
        execution_context = lancelot.MockSpec(name='execution_context')
        results = lancelot.MockSpec(name='results')
        make_instruction = Make('wrong params', wrong_params)
        spec = lancelot.Spec(make_instruction)
        spec.execute(execution_context, results).should_collaborate_with(
            execution_context.get_type('FakeClass').will_raise(type_error),
            results.failed(make_instruction, cause)
        )

    @lancelot.verifiable
    def handles_bad_import(self):
        ''' NoSuchClassException also indicates import problem '''
        wrong_params = ['creosote', 'FakeClass',
                        ['some unwanted', 'constructor args']
                       ]
        import_error = ImportError('y')
        cause = 'NO_CLASS FakeClass y'
        execution_context = lancelot.MockSpec(name='execution_context')
        results = lancelot.MockSpec(name='results')
        make_instruction = Make('wrong params', wrong_params)
        spec = lancelot.Spec(make_instruction)
        spec.execute(execution_context, results).should_collaborate_with(
            execution_context.get_type('FakeClass').will_raise(import_error),
            results.failed(make_instruction, cause)
        )

lancelot.grouping(MakeExceptionBehaviour)

@lancelot.verifiable
def call_invokes_method():
    ''' Call instruction should get an instance from context and execute a
    callable method on it, returning the results '''
    # Case where no args are supplied
    call = Call('id', ['instance', '__len__'])
    spec = lancelot.Spec(call)
    execution_context = lancelot.MockSpec(name='execution_context')
    results = lancelot.MockSpec(name='results')
    spec.execute(execution_context, results).should_collaborate_with(
            execution_context.get_instance('instance').will_return('mint'),
            results.completed(call, 4)
        )

    # Cases where args are supplied
    methods = {'method_0':[],
               'method_1':['1'],
               'method_2':['a', 'b']}
    for target in methods.keys():
        instance = lancelot.MockSpec(name='instance')
        result = ','.join([str(arg) for arg in methods[target]])
        execution_context = lancelot.MockSpec(name='execution_context')
        results = lancelot.MockSpec(name='results')
        params = ['instance', 'method', methods[target]]
        call_instruction = Call('id_90', params)
        spec = lancelot.Spec(call_instruction)
        spec.execute(execution_context, results).should_collaborate_with(
            execution_context.get_instance(params[0]).will_return(instance),
            instance.method(*tuple(params[2])).will_return(result),
            results.completed(call_instruction, result)
            )

@lancelot.verifiable
def call_substitutes_symbols():
    ''' Call instruction should perform variable substitution on its params '''
    execution_context = lancelot.MockSpec(name='execution_context')
    results = lancelot.MockSpec(name='results')
    instance = lancelot.MockSpec(name='instance')
    call_instruction = Call('with_symbol_substitution', 
                            ['instance', 'method', ['$A', '$b_', 'C$']])
    spec = lancelot.Spec(call_instruction)
    spec.execute(execution_context, results).should_collaborate_with(
            execution_context.get_instance('instance').will_return(instance),
            execution_context.get_symbol('A').will_return('X'),
            execution_context.get_symbol('b_').will_return('Y'),
            instance.method('X', 'Y', 'C$').will_return(42),
            results.completed(call_instruction, 42)
        )

class CallExceptionBehaviour(object):
    ''' Exception-related Specs for Call-instruction behaviour '''
    
    @lancelot.verifiable
    def handles_bad_instance(self):
        ''' NO_INSTANCE indicates bad instance name in Call ''' 
        execution_context = lancelot.MockSpec(name='execution_context')
        results = lancelot.MockSpec(name='results')
        params = ['bad_instance', 'method', 'args']
        cause = 'NO_INSTANCE bad_instance'
        call_instruction = Call('id_9A', params)
        spec = lancelot.Spec(call_instruction)
        spec.execute(execution_context, results).should_collaborate_with(
            execution_context.get_instance(params[0]).will_raise(KeyError),
            results.failed(call_instruction, cause)
            )

    @lancelot.verifiable
    def handles_bad_method(self):
        ''' NO_METHOD_IN_CLASS indicates bad method name for Call target ''' 
        execution_context = lancelot.MockSpec(name='execution_context')
        results = lancelot.MockSpec(name='results')
        params = ['instance', 'bad_method', 'args']
        instance = ClassWithNoArgs()
        cause = 'NO_METHOD_IN_CLASS bad_method ClassWithNoArgs'
        
        call_instruction = Call('id_9B', params)
        spec = lancelot.Spec(call_instruction)
        
        spec.execute(execution_context, results).should_collaborate_with(
            execution_context.get_instance(params[0]).will_return(instance),
            results.failed(call_instruction, cause)
            )
        
@lancelot.verifiable
def import_adds_to_pythonpath():
    ''' Import should add a path to the pythonpath when a path is supplied '''
    execution_context = lancelot.MockSpec('execution_context')
    results = lancelot.MockSpec('results')
    import_instruction = Import('id', ['/some_path'])
    spec = lancelot.Spec(import_instruction)
    spec.execute(execution_context, results).should_collaborate_with(
            execution_context.add_import_path('/some_path'),
            results.completed(import_instruction)
        )
    execution_context = lancelot.MockSpec('execution_context')
    results = lancelot.MockSpec('results')
    import_instruction = Import('id', ['c:\some_path'])
    spec = lancelot.Spec(import_instruction)
    spec.execute(execution_context, results).should_collaborate_with(
            execution_context.add_import_path('c:\some_path'),
            results.completed(import_instruction)
        )

@lancelot.verifiable
def import_adds_to_type_context():
    ''' Import should add a module / package to the type context 
    when one is supplied '''
    execution_context = lancelot.MockSpec('execution_context')
    results = lancelot.MockSpec('results')
    import_instruction = Import('id', ['some.module'])
    spec = lancelot.Spec(import_instruction)
    spec.execute(execution_context, results).should_collaborate_with(
            execution_context.add_type_prefix('some.module'),
            results.completed(import_instruction)
        )

lancelot.grouping(CallExceptionBehaviour)

@lancelot.verifiable
def call_and_assign_sets_variable():
    ''' CallAndAssign should assign a value to an execution context symbol '''
    execution_context = lancelot.MockSpec('execution_context')
    results = lancelot.MockSpec('results')
    call_and_assign = CallAndAssign('id', ['symbol', 'list', '__len__', []])
    spec = lancelot.Spec(call_and_assign)
    spec.execute(execution_context, results).should_collaborate_with(
            execution_context.get_instance('list').will_return([]),
            execution_context.store_symbol('symbol', 0),
            results.completed(call_and_assign, 0)
        )

if __name__ == '__main__':
    lancelot.verify()