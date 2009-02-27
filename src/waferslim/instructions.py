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
