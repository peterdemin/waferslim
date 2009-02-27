'''
Classes for turning instructions into a sequence of actions performed on 
the underlying system under test. 

The latest source code is available at http://code.launchpad.net/waferslim.

Copyright 2009 by the author(s). All rights reserved 
'''
import sys
from waferslim import WaferSlimException

class InstructionException(WaferSlimException):
    ''' Indicate an Instruction-related error ''' 
    pass
 
class NoSuchClassException(InstructionException):
    ''' Indicate an Make Instruction-related error ''' 
    pass

class NoSuchConstructorException(InstructionException):
    ''' Indicate an Make Instruction-related error ''' 
    pass

class NoSuchInstanceException(InstructionException):
    ''' Indicate a Call or CallAndAssign Instruction-related error ''' 
    pass

class NoSuchMethodException(InstructionException):
    ''' Indicate a Call or CallAndAssign Instruction-related error ''' 
    pass

class ExecutionContext(object):
    ''' Contextual execution environment to allow simultaneous code executions
    to take place without interfering with each other.
    TODO: see whether import hooks or similar can be used to isolate loaded
    modules across contexts: ?maybe with python 3.1 or 2.7? '''
    
    def __init__(self):
        ''' Set up the isolated context ''' 
        self._instances = {} 
    
    def get_type(self, fully_qualified_name):
        ''' Get a type instance from the context '''
        if fully_qualified_name in __builtins__:
            return __builtins__[fully_qualified_name]
        
        dot_pos = fully_qualified_name.rfind('.')
        if dot_pos == -1:
            msg = 'Type %s should be in a module' % fully_qualified_name
            raise TypeError(msg)

        module_part = fully_qualified_name[:dot_pos]
        type_part = fully_qualified_name[dot_pos + 1:]
        module = self.get_module(module_part)
        try:
            _type = getattr(module, type_part)
            return _type
        except AttributeError, e:
            msg = '%s could not be found in %s' % (type_part, module_part)
            raise TypeError(msg)

    def get_module(self, fully_qualified_name):
        ''' Perform nested module import / lookup as needed '''
        if fully_qualified_name in sys.modules:
            return sys.modules[fully_qualified_name]
        dot_pos = fully_qualified_name.rfind('.')
        if dot_pos == -1:
            return __import__(fully_qualified_name)
        else:
            parent_module = fully_qualified_name[:dot_pos]
            unqualified_name = fully_qualified_name[dot_pos + 1:]
            self.get_module(parent_module)
            return __import__(fully_qualified_name, 
                              fromlist=[unqualified_name])
    
    def store_instance(self, name, value):
        ''' Add a name=value pair to the context locals '''
        self._instances[name] = value

    def get_instance(self, name):
        ''' Get value from a name=value pair in the context locals '''
        return self._instances[name]
     
class Instruction(object):
    ''' Base class for instructions '''
    
    def __init__(self, instruction_id, params):
        ''' Specify the id of this instruction, and its params.
        Params must be a list. '''
        if not isinstance(params, list):
            raise TypeError('%r is not a list' % params)
        self._id = instruction_id
        self._params = params
        
    def instruction_id(self):
        ''' Return the id of this instruction '''
        return self._id
        
    def execute(self, execution_context, results):
        ''' Execute within the context and add to the results '''
#        raise InstructionException('Can only execute() a sub-class')
        pass

class Import(Instruction):
    ''' An "import <path>" instruction '''
    pass

class Make(Instruction):
    ''' A "make <instance>, <class>, <args>..." instruction '''
    
    def execute(self, execution_context, results):
        ''' Create a class instance and add it to the execution context ''' 
        try:
            target = execution_context.get_type(self._params[1])
        except (TypeError, ImportError), error:
            msg = '%s %s' % (self._params[1], error.args[0])
            results.raised(self, NoSuchClassException(msg))
            return
            
        args = tuple(self._params[2])
        try:
            instance = target(*args)
            execution_context.store_instance(self._params[0], instance)
            results.completed_ok(self)
        except TypeError, error:
            msg = '%s %s' % (self._params[1], error.args[0])
            results.raised(self, NoSuchConstructorException(msg))

class Call(Instruction):
    ''' A "call <instance>, <function>, <args>..." instruction '''
    
    def execute(self, execution_context, results):
        ''' Get an instance from the execution context and invoke a method'''
        try:
            instance = execution_context.get_instance(self._params[0])
        except KeyError:
            results.raised(self, NoSuchInstanceException(self._params[0]))
            return
        try:
            target = getattr(instance, self._params[1])
        except AttributeError:
            msg = '%s %s' % (self._params[1], type(instance))
            results.raised(self, NoSuchMethodException(msg))
            return
        args = tuple(self._params[2])
        result = target(*args)
        results.completed(self, result)

class CallAndAssign(Instruction):
    ''' A "callAndAssign <symbol>, <instance>, <function>, <args>..." 
    instruction '''
    pass
