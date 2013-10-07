'''
Classes for instantiating appropriate Instruction objects and executing them
in sequence, providing a context in which Instruction-s can be executed, and
collecting the results from each execution.

The latest source code is available at http://code.launchpad.net/waferslim.

Copyright 2009-2010 by the author(s). All rights reserved
'''
import os
import re
import sys
import logging
from .instructions import (Instruction,
                           Make,
                           Call,
                           CallAndAssign,
                           Import)
from .converters import to_string

_OK = 'OK'
_EXCEPTION = '__EXCEPTION__:'
_STOP_TEST = '%sABORT_SLIM_TEST:' % _EXCEPTION
_NONE_STRING = '/__VOID__/'


class Results(object):
    ''' Collecting parameter for results of Instruction execute() methods '''
    NO_RESULT_EXPECTED = object()

    def __init__(self, convert_to_string=to_string):
        ''' Set up the list to hold the collected results and obtain the
        currently registered type converters '''
        self._collected = []
        self._convert_to_string = convert_to_string

    def completed(self, instruction, result=NO_RESULT_EXPECTED):
        ''' An instruction has completed, perhaps with a result '''
        if result == Results.NO_RESULT_EXPECTED:
            str_result = _OK
        elif result is None:
            str_result = _NONE_STRING
        else:
            str_result = self._convert_to_string(result)
        self._collected.append([instruction.instruction_id(), str_result])

    def failed(self, instruction, cause, stop_test=False):
        ''' An instruction has failed due to some underlying cause '''
        failed_type = stop_test and _STOP_TEST or _EXCEPTION
        self._collected.append([instruction.instruction_id(),
                                '%s message:<<%s>>' % (failed_type, cause)])

    def collection(self):
        ''' Get the collected list of results - modifications to the list
        will not be reflected in this collection '''
        collected = []
        collected.extend(self._collected)
        return collected

_INSTRUCTION_TYPES = {'make': Make,
                      'import': Import,
                      'call': Call,
                      'callAndAssign': CallAndAssign}
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


def _debug(logger, msg, substitutions):
    ''' Log to logger a msg with potentially some substitutions '''
    try:
        logger.debug(msg % substitutions)
    except:
        logger.warn('Error logging %s:' % msg, exc_info=1)


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
            _debug(self._logger, 'Executing %r', instruction)
            try:
                instruction.execute(execution_context, results)
            except Exception:
                error = sys.exc_info()[1]
                self._logger.warn('Error executing %s:', instruction,
                                  exc_info=1)
                stop_test = 'stoptest' in type(error).__name__.lower()
                results.failed(instruction, error.args[0], stop_test)
                if stop_test:
                    break


class ParamsConverter(object):
    ''' Converter from (possibly nested) list of strings (possibly symbols)
    into (possibly nested) tuple of string arguments for invocation'''

    _SYMBOL_PATTERN = re.compile('\\$([a-zA-Z]\\w*)+', re.UNICODE)

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
        return ParamsConverter._SYMBOL_PATTERN.sub(
            self._match,
            possible_symbol,
            re.S
        )

    def _match(self, match):
        ''' Actually perform the substitution identified by the match '''
        if match:
            return self._execution_context.get_symbol(match.groups()[0])
        return ''


def to_pythonic(method_name):
    '''Converts CamelCase to pythonic_case'''
    return (method_name[0].lower() +
            ''.join(map(underscored_lowercase, method_name[1:])))


def to_lower_camel_case(method_name):
    '''Converts pythonic_case to camelCase'''
    camel_case = re.sub(
        '_(.)',
        lambda m: m.group(1).upper(),
        method_name
    )
    return camel_case[:1].lower() + camel_case[1:]


def to_upper_camel_case(method_name):
    '''Converts pythonic_case to CamelCase'''
    camel_case = re.sub(
        '_(.)',
        lambda m: m.group(1).upper(),
        method_name
    )
    return camel_case[:1].upper() + camel_case[1:]


def underscored_lowercase(char):
    if char.isupper():
        return '_' + char.lower()
    else:
        return char


class ExecutionContext(object):
    def __init__(self, params_converter=ParamsConverter,
                 logger=logging.getLogger('Execution')):
        self._params_converter = params_converter(self)
        self._logger = logger
        self.instances = {}
        self._symbols = {}
        self.classes = {}
        self.aliases = {}

    def get_type(self, fully_qualified_name):
        return self.classes.get(fully_qualified_name, None)

    def import_path(self, path):
        for name, data in load_classes(path):
            self.classes[name] = data['class']
            self.aliases[name] = ExecutionContext.get_aliases(data['methods'])

    @staticmethod
    def get_aliases(methods):
        aliases = dict((n, n) for n in methods)
        aliases.update(ExecutionContext.convention_aliases(aliases))
        return aliases

    @staticmethod
    def convention_aliases(aliases):
        camel_caseds = dict([
            (to_lower_camel_case(name), aliases[name])
            for name in aliases
        ])
        camel_caseds.update([
            (to_upper_camel_case(name), aliases[name])
            for name in aliases
        ])
        return camel_caseds

    def target_for(self, instance, method_name):
        class_name = instance.__class__.__name__
        method_name = self.aliases[class_name][method_name]
        if hasattr(instance, method_name):
            return getattr(instance, method_name)
        else:
            return None

    def store_instance(self, name, value):
        ''' Add a name=value pair to the context instances '''
        _debug(self._logger, 'Storing instance %s=%r', (name, value))
        self.instances[name] = value

    def get_instance(self, name):
        return self.instances.get(name, None)

    def store_symbol(self, name, value):
        _debug(self._logger, 'Storing symbol %s=%r', (name, value))
        self._symbols[name] = to_string(value)

    def get_symbol(self, name):
        if name in self._symbols:
            value = self._symbols[name]
            _debug(self._logger, 'Restoring symbol %s=%r', (name, value))
            return value
        else:
            return '$%s' % name

    def to_args(self, params, from_position):
        return self._params_converter.to_args(params, from_position)


def load_classes(package_path):
    on_path = find_in_sys_path(package_path)
    if on_path is not None:
        if os.path.isfile(on_path):
            for name, data in get_classes(load_source(on_path)):
                yield (name, data)
        else:
            for module in load_package(on_path):
                for name, data in get_classes(module):
                    yield (name, data)
    else:
        for name, data in get_classes(__import__(package_path)):
            yield (name, data)


def find_in_sys_path(path):
    for base in sys.path:
        rel_path = os.path.join(base, path)
        if os.path.exists(rel_path):
            return rel_path
    return None


def load_source(source_path):
    import imp
    name = os.path.splitext(os.path.basename(source_path))[0]
    return imp.load_source(name, source_path)


def load_package(package_path):
    import pkgutil
    for loader, name, is_pkg in pkgutil.iter_modules([package_path]):
        if is_pkg:
            subpackage_path = os.path.join(package_path, name)
            for module in load_package(subpackage_path):
                yield module
        else:
            yield loader.find_module(name).load_module(name)


def get_classes(module):
    import inspect
    import six
    if six.PY2:
        def isfunction(a):
            return inspect.ismethod(a) or inspect.isfunction(a)
    elif six.PY3:
        isfunction = inspect.isfunction
    for class_name, Class in inspect.getmembers(module, inspect.isclass):
        methods = [n
                   for n, _ in inspect.getmembers(Class, isfunction)
                   if '__' not in n]
        yield (class_name, {'class': Class, 'methods': methods})
