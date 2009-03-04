'''
Instruction classes that invoke actions on some underlying "system under test".

The latest source code is available at http://code.launchpad.net/waferslim.

Copyright 2009 by the author(s). All rights reserved 
'''
import re

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
    
    def __repr__(self):
        ''' Return a meaningful representation of the Instruction '''
        return '%s %s: %s' % (type(self).__name__, self._id, self._params) 
        
    def execute(self, execution_context, results):
        ''' Base execute() is only called when the instruction type
        was unrecognised -- fail with _BAD_INSTRUCTION '''
        results.failed(self, '%s %s' % (_BAD_INSTRUCTION, self._params[0]))

class Import(Instruction):
    ''' An "import <path or module context>" instruction '''
    
    def execute(self, execution_context, results):
        ''' Adds an imported path or module context to the execution context'''
        path_or_module = self._params[0]
        if self._ispath(path_or_module):
            execution_context.add_import_path(path_or_module)
        else:
            execution_context.add_type_prefix(path_or_module)
        results.completed(self)
        
    def _ispath(self, possible_path):
        ''' True if this is a path, False otherwise '''
        return possible_path.find('/') != -1 or possible_path.find('\\') != -1

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
            
        try:
            args = tuple(self._params[2])
        except IndexError:
            args = ()
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
    _PATTERN = re.compile('\\$([a-zA-Z]\\w*)', re.UNICODE)
    
    def execute(self, execution_context, results):
        ''' Delegate to _invoke_call then record results on completion '''
        result, failed = self._invoke(execution_context, results, self._params)
        if failed:
            return
        results.completed(self, result)
        
    def _invoke(self, execution_context, results, params):
        ''' Get an instance from the execution context and invoke a method'''
        try:
            instance = execution_context.get_instance(params[0])
        except KeyError:
            results.failed(self, '%s %s' % (_NO_INSTANCE, params[0]))
            return (None, True)
        try:
            target = getattr(instance, params[1])
        except AttributeError:
            cause = '%s %s %s' % (_NO_METHOD, params[1], 
                                  type(instance).__name__)
            results.failed(self, cause)
            return (None, True)
        try:
            args = self._make_args(execution_context, params[2])
        except IndexError:
            args = ()
        result = target(*args)
        return (result, False)
    
    def _make_args(self, execution_context, args_list):
        ''' make a tuple of args from a list containing values and symbols'''
        if isinstance(args_list, list):
            args_without_symbols = [self._nonsymbolic(execution_context, arg) \
                                    for arg in args_list]
            return tuple(args_without_symbols)
        return (self._nonsymbolic(execution_context, args_list),)
    
    def _nonsymbolic(self, execution_context, possible_symbol):
        ''' perform any symbol substitution on a possible_symbol '''
        match = Call._PATTERN.match(possible_symbol)
        if match:
            return execution_context.get_symbol(match.groups()[0])
        return possible_symbol

class CallAndAssign(Call):
    ''' A "callAndAssign <symbol>, <instance>, <function>, <args>..." 
    instruction '''

    def execute(self, execution_context, results):
        ''' Delegate to _invoke_call then set variable and record results 
        on completion '''
        params = []
        params.extend(self._params)
        symbol_name = params.pop(0)
        result, failed = self._invoke(execution_context, results, params)
        if failed:
            return
        execution_context.store_symbol(symbol_name, result)
        results.completed(self, result)
