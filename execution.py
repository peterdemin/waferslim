'''
Classes for instantiating appropriate Instruction objects and executing them
in sequence, providing a context in which Instruction-s can be executed, and
collecting the results from each execution.

The latest source code is available at http://code.launchpad.net/waferslim.

Copyright 2009-2010 by the author(s). All rights reserved
'''
import logging
import re
import sys
from instructions import (Instruction,
                          Make,
                          Call,
                          CallAndAssign,
                          Import)
from converters import to_string

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


def pythonic(method_name):
    ''' Returns a method_name converted from camelCase to pythonic_case'''
    return method_name[0].lower() + \
        ''.join([_underscored_lowercase(char) for char in method_name[1:]])


def _underscored_lowercase(char):
    ''' Returns _<lowercase char> if char is uppercase; char otherwise'''
    if char.isupper():
        return '_%s' % char.lower()
    return char


class ExecutionContext(object):
    def __init__(self, params_converter=ParamsConverter,
                 logger=logging.getLogger('Execution')):
        self._instances = {}
        self._symbols = {}
        self._params_converter = params_converter(self)
        self._logger = logger
        self.classes = {}

    def get_type(self, fully_qualified_name):
        return self.classes[fully_qualified_name]

    def add_import_path(self, path):
        self.classes = load_classes(path)

    def target_for(self, instance, method_name, convert_name=True):
        ''' Return an instance's named method to use as a call target.
        If a pythonically_named method exists it will be used, otherwise the
        fitnesse standard camelCase method will be returned it it exists. '''
        try:
            return getattr(instance,
                           convert_name
                           and pythonic(method_name)
                           or method_name)
        except AttributeError:
            return (convert_name
                    and self.target_for(instance, method_name, False)
                    or None)

    def store_instance(self, name, value):
        ''' Add a name=value pair to the context instances '''
        _debug(self._logger, 'Storing instance %s=%r', (name, value))
        self._instances[name] = value

    def get_instance(self, name):
        ''' Get value from a name=value pair in the context instances '''
        try:
            return self._instances[name]
        except KeyError:
            return None

    def store_symbol(self, name, value):
        ''' Add a name=value pair to the context symbols '''
        _debug(self._logger, 'Storing symbol %s=%r', (name, value))
        self._symbols[name] = to_string(value)

    def get_symbol(self, name):
        ''' Get value from a name=value pair in the context symbols '''
        try:
            value = self._symbols[name]
            _debug(self._logger, 'Restoring symbol %s=%r', (name, value))
            return value
        except KeyError:
            return '$%s' % name

    def to_args(self, params, from_position):
        ''' Delegate args construction to the ParamsConverter '''
        return self._params_converter.to_args(params, from_position)


def load_classes(package_path):
    import os
    if os.path.exists(package_path):
        classes = {}
        if os.path.isfile(package_path):
            classes.update(get_classes(load_source(package_path)))
        else:
            for module in load_package(package_path):
                classes.update(get_classes(module))
        return classes
    else:
        return get_classes(__import__(package_path))


def load_source(source_path):
    import os
    import imp
    name = os.path.splitext(os.path.basename(source_path))[0]
    return imp.load_source(name, source_path)


def load_package(package_path):
    import os
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
    return dict(inspect.getmembers(module, inspect.isclass))
