'''
Classes for turning instructions into a sequence of actions performed on 
the underlying system under test. 

The latest source code is available at http://code.launchpad.net/waferslim.

Copyright 2009 by the author(s). All rights reserved 
'''
import sys
from waferslim import WaferSlimException
from waferslim.instructions import InstructionException, \
        NoSuchClassException, NoSuchConstructorException, \
        NoSuchInstanceException, NoSuchMethodException, \
        Make, Call, CallAndAssign, Import

_OK = 'OK'
_EXCEPTION = '__EXCEPTION__:'
_EXCEPTIONS = {InstructionException:'MALFORMED_INSTRUCTION',
               NoSuchClassException:'NO_CLASS',
               NoSuchConstructorException:'COULD_NOT_INVOKE_CONSTRUCTOR',
               NoSuchInstanceException: 'NO_INSTANCE',
               NoSuchMethodException:'NO_METHOD_IN_CLASS'
               }

_NONE_STRING = '/__VOID__/'

class Results(object):
    ''' Collecting parameter for results of Instruction execute() methods '''
    NO_RESULT = object()
    
    def __init__(self):
        ''' Set up the list to hold the collected results '''
        self._collected = []
    
    def completed(self, instruction, result=NO_RESULT):
        ''' An instruction has completed, perhaps with a result '''
        if result == Results.NO_RESULT:
            str_result = _OK
        elif result:
            str_result = str(result)
        else:
            str_result = _NONE_STRING
        self._collected.append([instruction.instruction_id(), str_result])
        
    def raised(self, instruction, exception):
        ''' An instruction has raised an exception. The nature of the
        exception will be translated into the relevant Slim protocol format.'''
        self._collected.append([instruction.instruction_id(), 
                                self._translate(exception)])
    
    def _translate(self, exception):
        ''' Translate an exception type into a formatted message '''
        return '%s message:<<%s %s>>' % (_EXCEPTION, 
                                         _EXCEPTIONS[type(exception)], 
                                         exception.args[0])
    
    def collection(self):
        ''' Get the collected list of results - modifications to the list 
        will not be reflected in this collection '''
        collected = []
        collected.extend(self._collected)
        return collected

_INSTRUCTION_TYPES = {'make':Make,
                      'import':Import,
                      'call':Call,
                      'callAndAssign':CallAndAssign }
_ID_POSITION = 0
_TYPE_POSITION = 1

def instruction_for(params):
    ''' Factory method for Instruction types '''
    instruction_type = params.pop(_TYPE_POSITION)
    instruction_id = params.pop(_ID_POSITION)
    return _INSTRUCTION_TYPES[instruction_type](instruction_id, params)

class Instructions(object):
    ''' Container for executable sequence of Instruction-s '''
    
    def __init__(self, unpacked_list, factory_method=instruction_for):
        ''' Provide an unpacked list of strings that will be converted 
        into a sequence of Instruction-s to execute '''
        self._unpacked_list = unpacked_list
        self._instruction_for = factory_method
    
    def execute(self, execution_context, results):
        ''' Create and execute Instruction-s, collecting the results '''
        for item in self._unpacked_list:
            instruction = self._instruction_for(item)
            instruction.execute(execution_context, results)
     
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
        except AttributeError:
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
