'''
Classes for turning instructions into a sequence of actions performed on 
the underlying system under test. 

The latest source code is available at http://code.launchpad.net/waferslim.

Copyright 2009 by the author(s). All rights reserved 
'''

_BAD_INSTRUCTION = 'INVALID_STATEMENT'
_NO_CLASS = 'NO_CLASS'
_NO_CONSTRUCTION = 'COULD_NOT_INVOKE_CONSTRUCTOR'
_NO_INSTANCE = 'NO_INSTANCE'
_NO_METHOD = 'NO_METHOD_IN_CLASS'

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
        ''' Base execute() is only called when the instruction type
        was unrecognised -- fail with _BAD_INSTRUCTION '''
        results.failed(self, '%s %s' % (_BAD_INSTRUCTION, self._params[0]))

class Import(Instruction):
    ''' An "import <path>" instruction '''
    
    def execute(self, execution_context, results):
        ''' Adds the imported path to the execution context '''
        path = self._params[0]
        execution_context.add_import_path(path)
        results.completed(self)

class Make(Instruction):
    ''' A "make <instance>, <class>, <args>..." instruction '''
    
    def execute(self, execution_context, results):
        ''' Create a class instance and add it to the execution context ''' 
        try:
            target = execution_context.get_type(self._params[1])
        except (TypeError, ImportError), error:
            cause = '%s %s %s' % (_NO_CLASS, self._params[1], error.args[0])
            results.failed(self, cause)
            return
            
        args = tuple(self._params[2])
        try:
            instance = target(*args)
            execution_context.store_instance(self._params[0], instance)
            results.completed(self)
        except TypeError, error:
            cause = '%s %s %s' % (_NO_CONSTRUCTION, 
                                  self._params[1], error.args[0])
            results.failed(self, cause)

class Call(Instruction):
    ''' A "call <instance>, <function>, <args>..." instruction '''
    
    def execute(self, execution_context, results):
        ''' Get an instance from the execution context and invoke a method'''
        try:
            instance = execution_context.get_instance(self._params[0])
        except KeyError:
            results.failed(self, '%s %s' % (_NO_INSTANCE, self._params[0]))
            return
        try:
            target = getattr(instance, self._params[1])
        except AttributeError:
            cause = '%s %s %s' % (_NO_METHOD, self._params[1], 
                                  type(instance).__name__)
            results.failed(self, cause)
            return
        args = tuple(self._params[2])
        result = target(*args)
        results.completed(self, result)

class CallAndAssign(Instruction):
    ''' A "callAndAssign <symbol>, <instance>, <function>, <args>..." 
    instruction '''
    pass
