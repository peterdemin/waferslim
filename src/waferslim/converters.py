'''
Classes for converting to/from strings and python types, in a manner similar
to that described at http://fitnesse.org/FitNesse.SliM.CustomTypes.

Import this module and use convert_arg() as a method decorator 
in your own classes (such as decision_table.py in the examples).

Converters are provided for bool, int, float and datetime (date, time 
and datetime) types. You may also register your own custom converter with
this module using add_converter(), after which it will be accessible both
to decorated methods and to the waferslim code that translates return values
into standard slim strings.

The latest source code is available at http://code.launchpad.net/waferslim.

Copyright 2009 by the author(s). All rights reserved 
'''

import datetime

__ALL_CONVERTERS = {} # The registered converters, keyed on type

class Converter(object):
    ''' Base class for converting to/from strings from/to python types'''
    
    def to_string(self, value):
        ''' Use default str() to convert from a value into a string '''
        return str(value)
    
    def from_string(self, value):
        ''' NotImplemented! '''
        msg = 'from_string() must be implemented in subclasses'
        raise NotImplementedError(msg)

__DEFAULT_CONVERTER = Converter() # Use as default (when no type-specific 
                                  # instance is present in __ALL_CONVERTERS)  

class BoolConverter(Converter):
    ''' Converter to/from bool type '''
    
    def from_string(self, value):
        ''' yes/Yes or true/True are bool True; anything else is False '''
        return value.lower() in ['yes', 'true']
    
    def to_string(self, value):
        ''' "yes" if value==bool True; "no" otherwise '''
        return value==True and 'yes' or 'no'

class FromConstructorConverter(Converter):
    ''' Converter for types that implement __new__(str) e.g. int and float '''
    
    def __init__(self, _type):
        ''' Specify the _type whose constructor will be used'''
        self._type = _type

    def from_string(self, value):
        ''' Delegate to the type(str) constructor to perform the conversion '''
        return self._type(value)

def add_converter(for_type, converter_instance):
    ''' Register a converter_instance to be used with for_type instances.
    The converter must implement from_string() and to_string(). '''
    if hasattr(converter_instance, 'from_string') and \
    hasattr(converter_instance, 'to_string'):
        __ALL_CONVERTERS[for_type] = converter_instance
        return
    msg = 'Converter for %s requires from_string() and to_string()' % for_type
    raise TypeError(msg)

# Register the standard converters for bool, int, float and datetime types
add_converter(bool, BoolConverter())
add_converter(int, FromConstructorConverter(int))
add_converter(float, FromConstructorConverter(float))
#                  datetime.date: DateConverter(),
#                  datetime.time: TimeConverter(),
#                  datetime.datetime: DatetimeConverter(),

def convert_arg(to_type):
    ''' Method decorator to convert a slim-standard string arg to a specific
    python datatype "to_type". Delegates to from_string() method on a 
    type-specific Converter added through this module.'''
    def conversion_decorator(fn):
        ''' callable that performs the actual decoration '''
        converter = __ALL_CONVERTERS[to_type]
        return lambda self, value: fn(self, converter.from_string(value))
    return conversion_decorator

def convert_value(value):
    ''' Convert from a typed value to a string value with to_string().
    Try to use a registered type-specific converter if one exists,
    otherwise use the default (base Converter).''' 
    try:
        return __ALL_CONVERTERS[type(value)].to_string(value)
    except KeyError:
        return __DEFAULT_CONVERTER.to_string(value)