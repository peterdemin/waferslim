'''
Classes for converting to/from strings and python types, in a manner similar
to that described at http://fitnesse.org/FitNesse.SliM.CustomTypes.

Import this module and use the method decorators 
    convert_arg(to_type=...) 
    convert_arg(using=...)
    convert_result(using=...) 
in your own classes (see decision_table and script_table in the examples).

Converters are provided for bool, int, float and datetime (date, time 
and datetime) types. You may also register your own custom converter with
this module using register_converter(), after which it will be accessible both
to decorated methods and to the waferslim code that translates return values
into standard slim strings.

The latest source code is available at http://code.launchpad.net/waferslim.

Copyright 2009 by the author(s). All rights reserved 
'''

import datetime, threading

__THREADLOCAL = threading.local()

class Converter(object):
    ''' Base class for converting to/from strings from/to python types'''
    
    def to_string(self, value):
        ''' Use default str() to convert from a value into a string '''
        return str(value)
    
    def from_string(self, value):
        ''' NotImplemented! '''
        msg = 'from_string(%s) must be implemented in subclasses' % value
        raise NotImplementedError(msg)

_DEFAULT_CONVERTER = Converter() # Use as default (when no type-specific 
                                  # instance is present in converters)  

class StrConverter(Converter):
    ''' "Converter" (really a Null-Converter) to/from str type.
    Only used by methods whose arguments have multiple types.'''
    def from_string(self, value):
        ''' The value is already a string so simply return it'''
        return value

class TrueFalseConverter(Converter):
    ''' Converter to/from bool type using true/false. This is the standard.'''
    
    def from_string(self, value):
        ''' true/True are bool True; anything else is False '''
        return value.lower() == 'true'
    
    def to_string(self, value):
        ''' "true" if value==bool True; "false" otherwise '''
        return value == True and 'true' or 'false'

class YesNoConverter(Converter):
    ''' Converter to/from bool type using yes/no. Offered as an alternative
    to TrueFalseConverter.'''
    
    def from_string(self, value):
        ''' yes/Yes are bool True; anything else is False '''
        return value.lower() == 'yes'
    
    def to_string(self, value):
        ''' "yes" if value==bool True; "no" otherwise '''
        return value == True and 'yes' or 'no'
    
class FromConstructorConverter(Converter):
    ''' Converter for types that implement __new__(str) e.g. int and float '''
    
    def __init__(self, _type):
        ''' Specify the _type whose constructor will be used'''
        Converter.__init__(self)
        self._type = _type

    def from_string(self, value):
        ''' Delegate to the type(str) constructor to perform the conversion '''
        return self._type(value)
    
class DateConverter(Converter):
    ''' Converter to/from datetime.date type via iso-standard format 
    (4digityear-2digitmonth-2digitday, e.g. 2009-02-28) '''
    
    def from_string(self, value):
        ''' Generate datetime.date from iso-standard format str '''
        iso_parts = [int(part) for part in value.split('-')]
        return datetime.date(*tuple(iso_parts))

class TimeConverter(Converter):
    ''' Converter to/from datetime.date type via iso-standard format 
    (2digithour:2digitminute:2digitsecond - with or without
    an additional optional .6digitmillis, e.g. 01:02:03 or 01:02:03.456789).
    Does not take any time-zone UTC offset into account!'''
    
    def from_string(self, value):
        ''' Generate datetime.time from iso-standard format str '''
        iso_parts = [int(part) for part in self._timesplit(value)]
        return datetime.time(*tuple(iso_parts))
    
    def _timesplit(self, value):
        ''' split() value at both : and . characters per iso time format'''
        dot_pos = value.rfind('.')
        if dot_pos == -1:
            return value.split(':')
        else:
            parts = self._timesplit(value[:dot_pos])
            parts.append(value[dot_pos+1:])
            return parts

class DatetimeConverter(Converter):
    ''' Converter to/from datetime.datetime type via iso-standard formats 
    ("dateformat<space>timeformat", e.g. "2009-02-28 21:54:32.987654").
    Delegates most of the actual work to DateConverter and TimeConverter. '''

    def from_string(self, value):
        ''' Generate a datetime.datetime from a str '''
        # TODO: ?use datetime.datetime.strptime instead
        date_part, time_part = value.split(' ')
        the_date = converter_for(datetime.date).from_string(date_part)
        the_time = converter_for(datetime.time).from_string(time_part)
        return datetime.datetime.combine(the_date, the_time)

#TODO: ?from_string might be nice for table_table?
class IterableConverter(Converter):
    ''' Converter to/from an iterable type (e.g. list, tuple). 
    Delegates to type-specific converters for each item in the list.'''
    
    def to_string(self, iterable_values):
        ''' Generate a list of str values from a list of typed values.
        Note the slightly misleading name of this method: it actually returns
        a list (of str) rather than an actual str...'''
        return [converter_for(value).to_string(value) \
                for value in iterable_values]

def register_converter(for_type, converter_instance):
    ''' Register a converter_instance to be used with all for_type instances.
    Registration is 'forever' (across all fitnesse tables run as a suite): the
    decision_table example demonstrates how to use an alternative converter 
    'temporarily' (for a single fitnesse table within a suite).  
    A converter_instance must implement from_string() and to_string(). '''
    if hasattr(converter_instance, 'from_string') and \
    hasattr(converter_instance, 'to_string'):
        __init_converters()
        __THREADLOCAL.converters[for_type] = converter_instance
        return
    msg = 'Converter for %s requires from_string() and to_string()' % for_type
    raise TypeError(msg)

def __init_converters():
    ''' Ensure standard converters exist for bool, int, float, datetime, ...
    All registered converters, keyed on type, are held as thread-local to 
    ensure that ExecutionContext-s (which are created per thread by the 
    server) really are isolated from each other when the server is run 
    in keepalive (multi-user) mode'''
    if hasattr(__THREADLOCAL, 'converters'):
        return
    
    __THREADLOCAL.converters = {} 
    register_converter(bool, TrueFalseConverter())
    register_converter(int, FromConstructorConverter(int))
    register_converter(float, FromConstructorConverter(float))
    register_converter(datetime.date, DateConverter())
    register_converter(datetime.time, TimeConverter())
    register_converter(datetime.datetime, DatetimeConverter())
    register_converter(list, IterableConverter())
    register_converter(tuple, IterableConverter())
    register_converter(str, StrConverter())

def convert_arg(to_type=None, using=None):
    ''' Method decorator to convert a slim-standard string arg to a specific
    python datatype. Only 1 of "to_type" or "using" should be supplied. 
    If "to_type" is supplied then a type-specific Converter is found from
    those added through this module. If "using" is supplied then the arg
    is taken as the converter to be used - however this converter will only
    be used 'temporarily' (not 'forever', as it would have been if 
    register_converter() had been called.) 
    "to_type" and "using" may be supplied as single objects, in which case
    the same conversion strategy will be applied to each argument in the target
    method, e.g. 
        @convert_arg(to_type=int)
        def some_method(self, an_int, another_int)...
    or they may be suppplied as iterables, in which case they will be iterated
    over to provide a different converter for each argument in the target 
    method, e.g. 
        @convert_arg(to_type=(int, float))
        def some_method(self, an_int, a_float)...
    '''
    conversion_strategy = to_type and to_type or using
    if not conversion_strategy:
        raise TypeError('One of "to_type" or "using" must be supplied')
    def conversion_decorator(fn):
        ''' callable that performs the actual decoration '''
        if hasattr(conversion_strategy, '__iter__'):
            converter = using and using or \
                        [_strict_converter_for(_type) for _type in to_type]
            next = converter.__iter__().next
        else:
            converter = using and using or _strict_converter_for(to_type)
            next = lambda: converter
        return lambda self, *args: \
                fn(self, *tuple([next().from_string(arg) for arg in args]))
    return conversion_decorator

def convert_result(using):
    ''' Method decorator to convert a method result from a python datatype 
    using a specific converter. The argument "using" is required.
    Ordinarily this decorator is not needed by client code,
    as result conversion is performed automatically using an appropriate
    converter registered for the datatype of the result value. It is included
    for specific conversion done 'temporarily' for a single fitnesse table 
    within a suite '''
    if not (using):
        raise TypeError('"using" converter must be supplied')
    def conversion_decorator(fn):
        ''' callable that performs the actual decoration '''
        return lambda self, *args: using.to_string(fn(self, *args))
    return conversion_decorator

def converter_for(type_or_value): 
    ''' Returns the appropriate converter for a particular type_or_value.
    This will be a registered type-specific converter if one exists,
    otherwise the default (base Converter).''' 
    try:
        return _strict_converter_for(type_or_value)
    except KeyError:
        return _DEFAULT_CONVERTER
    
def _strict_converter_for(type_or_value): 
    ''' Returns the exact converter for a particular type_or_value.
    This will be a registered type-specific converter if one exists,
    otherwise a KeyError will be raised.'''
    __init_converters() 
    try:
        return __THREADLOCAL.converters[type_or_value]
    except (KeyError, TypeError):
        return __THREADLOCAL.converters[type(type_or_value)]