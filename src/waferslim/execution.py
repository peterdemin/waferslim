'''
Classes for instantiating appropriate Instruction objects and executing them
in sequence, providing a context in which Instruction-s can be executed, and 
collecting the results from each execution.

The latest source code is available at http://code.launchpad.net/waferslim.

Copyright 2009 by the author(s). All rights reserved 
'''
import __builtin__, logging, re, sys, threading
from waferslim.instructions import Instruction, \
                                   Make, Call, CallAndAssign, Import
from waferslim.converters import converter_for

_OK = 'OK'
_EXCEPTION = '__EXCEPTION__:'

_NONE_STRING = '/__VOID__/'

class Results(object):
    ''' Collecting parameter for results of Instruction execute() methods '''
    NO_RESULT_EXPECTED = object()
    
    def __init__(self, converter=converter_for):
        ''' Set up the list to hold the collected results and obtain the
        currently registered type converters '''
        self._collected = []
        self._converter = converter
    
    def completed(self, instruction, result=NO_RESULT_EXPECTED):
        ''' An instruction has completed, perhaps with a result '''
        if result == Results.NO_RESULT_EXPECTED:
            str_result = _OK
        elif result == None:
            str_result = _NONE_STRING
        else:
            str_result = self._converter(result).to_string(result)
        self._collected.append([instruction.instruction_id(), str_result])
        
    def failed(self, instruction, cause):
        ''' An instruction has failed due to some underlying cause '''
        self._collected.append([instruction.instruction_id(), 
                                self._format(cause)])
    
    def _format(self, cause):
        ''' Return a failure cause in protocol exception format '''
        return '%s message:<<%s>>' % (_EXCEPTION, cause)
    
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
    try:
        return _INSTRUCTION_TYPES[instruction_type](instruction_id, params)
    except KeyError:
        return Instruction(instruction_id, [instruction_type])

class Instructions(object):
    ''' Container for executable sequence of Instruction-s '''
    
    def __init__(self, unpacked_list, factory_method=instruction_for):
        ''' Provide an unpacked list of strings that will be converted 
        into a sequence of Instruction-s to execute '''
        self._unpacked_list = unpacked_list
        self._instruction_for = factory_method
        self._logger = logging.getLogger('Instructions')
    
    def execute(self, execution_context, results):
        ''' Create and execute Instruction-s, collecting the results '''
        for item in self._unpacked_list:
            instruction = self._instruction_for(item)
            self._debug(instruction)
            try:
                instruction.execute(execution_context, results)
            except Exception, error:
                self._logger.warn('Error executing %s:', instruction, 
                                  exc_info=1)
                results.failed(instruction, error.args[0])
    
    def _debug(self, instruction):
        ''' Log a debug message about the execution of Instruction-s '''
        self._logger.debug('Executing %r' % instruction)

class ParamsConverter(object):
    ''' Converter from (possibly nested) list of strings (possibly symbols)
    into (possibly nested) tuple of string arguments for invocation''' 
    
    _SYMBOL_PATTERN = re.compile('\\$([a-zA-Z]\\w*)', re.UNICODE)
    
    def __init__(self, execution_context):
        ''' Provide the execution_context for symbol lookup '''
        self._execution_context = execution_context
        
    def to_args(self, params, from_position):
        ''' Convert params[from_postition:] to args tuple ''' 
        args = [self._lookup_symbol(param) for param in params[from_position:]]
        return tuple(args)
    
    def _lookup_symbol(self, possible_symbol):
        ''' Lookup (recursively if required) a possible symbol '''
        if isinstance(possible_symbol, list):
            return self.to_args(possible_symbol, 0)
        
        match = ParamsConverter._SYMBOL_PATTERN.match(possible_symbol)
        if match:
            return self._execution_context.get_symbol(match.groups()[0])
        return possible_symbol
   
class ExecutionContext(object):
    ''' Contextual execution environment to allow simultaneous code executions
    to take place in isolation from each other - see keepalive startup arg.'''
    
    _SEMAPHORE = threading.Semaphore()
    _REAL_IMPORT = __builtin__.__import__
    _SYSPATH = sys.path
    
    def __init__(self, params_converter = ParamsConverter, isolate_imports=False):
        ''' Set up the isolated context '''
        # Fitnesse-specific... 
        self._instances = {}
        self._libraries = {} 
        self._symbols = {} 
        self._path = []
        self._type_prefixes = []
        self._params_converter = params_converter(self)
        # Implementation-specific...
        self._logger=logging.getLogger('Execution')
        self._isolate_imports = isolate_imports
        self._imported = {}
        self._modules = {}
        self._modules.update(sys.modules)
    
    def get_type(self, fully_qualified_name):
        ''' Get a type instance from the context '''        
        dot_pos = fully_qualified_name.rfind('.')
        if dot_pos == -1:
            for prefix in self._type_prefixes:
                try:
                    prefixed_name = '%s.%s' % (prefix, fully_qualified_name)
                    return self.get_type(prefixed_name)
                except (TypeError, ImportError):
                    pass
            msg = 'Type %s is not in a module: perhaps you want to Import it?'
            raise TypeError(msg % fully_qualified_name)

        module_part = fully_qualified_name[:dot_pos]
        type_part = fully_qualified_name[dot_pos + 1:]
        module = self.get_module(module_part)
        try:
            _type = getattr(module, type_part)
            return _type
        except AttributeError:
            msg = '%s could not be found in %s' % (type_part, module_part)
            raise TypeError(msg)
        
    def add_type_prefix(self, prefix):
        ''' Add a prefix that may be used to find classes without using long
        fully-dot-qualified names'''
        self._type_prefixes.append(prefix)

    def get_module(self, fully_qualified_name):
        ''' Monkey-patch builtin __import__ and sys.path to ensure isolation
        of the context and do so in a way that prevents multiple contexts
        trying to monkey-patch simultaneously; perform import / lookup of
        the module; then reset the global environment including del() of 
        imported modules from sys.modules '''
        ExecutionContext._SEMAPHORE.acquire()
        try:
            if self._isolate_imports: __builtin__.__import__ = self._import
            sys.path = self._path
            sys.path.extend(ExecutionContext._SYSPATH)
            
            return self._import_module(fully_qualified_name)
        finally:
            sys.path = ExecutionContext._SYSPATH
            if self._isolate_imports: 
                __builtin__.__import__ = ExecutionContext._REAL_IMPORT
                self.cleanup_imports()
            ExecutionContext._SEMAPHORE.release()
                
    def cleanup_imports(self):
        ''' Clean-up imports '''
        for mod in self._imported.keys():
            try:
                del(sys.modules[mod])
            except KeyError:
                pass
            self._imported = {}
    
    def _import_module(self, fully_qualified_name):
        ''' Actually perform nested module import / lookup of a module '''
        dot_pos = fully_qualified_name.rfind('.')
        if dot_pos == -1:
            return self._import(fully_qualified_name)
        else:
            parent_module = fully_qualified_name[:dot_pos]
            unqualified_name = fully_qualified_name[dot_pos + 1:]
            self._import_module(parent_module)
            return self._import(fully_qualified_name, 
                                fromlist=[str(unqualified_name)])
    
    def _import(self, *args, **kwds):
        ''' If module has already been imported, return it. Otherwise delegate
        to builtin __import__ and keep note of the imported module.'''
        try:
            return self._modules[args[0]]
        except KeyError:
            pass
        self._logger.info('Importing %s%s' 
                           % (self._isolate_imports and 'isolated ' or '', 
                              args[0]))
        mod = ExecutionContext._REAL_IMPORT(*args, **kwds)
        self._imported[mod.__name__] = mod
        self._modules[mod.__name__] = mod
        return mod
    
    def get_library_method(self, name):
        ''' Get a method from the library '''
        self._logger.debug('Getting library method %s' % name)
        for instance in self._libraries.values():
            if hasattr(instance, name):
                return getattr(instance, name)
        err = 'No library method %s found. Are you missing a Library table?' 
        raise AttributeError(err % name)
    
    def _store_library_instance(self, name, value):
        ''' Add methods in a class instance to the library '''
        self._logger.debug('Storing library instance %s=%s' % (name, value))
        self._libraries[name] = value
    
    def _is_library(self, name):
        ''' Determine whether an instance name represents a library '''
        return name.lower().startswith("library")
    
    def store_instance(self, name, value):
        ''' Add a name=value pair to the context instances '''
        if (self._is_library(name)):
            self._store_library_instance(name, value)
        else:
            self._logger.debug('Storing instance %s=%s' % (name, value))
            self._instances[name] = value

    def get_instance(self, name):
        ''' Get value from a name=value pair in the context instances '''
        return self._instances[name]
    
    def add_import_path(self, path):
        ''' An an import location to the context path '''
        self._path.append(path)
    
    def store_symbol(self, name, value):
        ''' Add a name=value pair to the context symbols '''
        self._logger.debug('Storing symbol %s=%s' % (name, value))
        self._symbols[name] = value

    def get_symbol(self, name):
        ''' Get value from a name=value pair in the context symbols '''
        return self._symbols[name]
    
    def to_args(self, params, from_position):
        ''' Delegate args construction to the ParamsConverter '''
        return self._params_converter.to_args(params, from_position)
