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

_ALL_CONVERTERS = {} # The registered converters, keyed on type

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
                                  # instance is present in _ALL_CONVERTERS)  

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
    
class DateConverter(Converter):
    ''' Converter to/from datetime.date type via iso-standard format 
    (4digityear-2digitmonth-2digitday, e.g. 2009-02-28) '''
    def from_string(self, value):
        iso_parts = [int(part) for part in value.split('-')]
        return datetime.date(*tuple(iso_parts))

class TimeConverter(Converter):
    ''' Converter to/from datetime.date type via iso-standard format 
    (2digithour:2digitminute:2digitsecond - with or without
    an additional optional .6digitmillis, e.g. 01:02:03 or 01:02:03.456789).
    Does not take any time-zone UTC offset into account!'''
    def from_string(self, value):
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
        # TODO: ?use datetime.datetime.strptime instead
        date_part, time_part = value.split(' ')
        the_date = _ALL_CONVERTERS[datetime.date].from_string(date_part)
        the_time = _ALL_CONVERTERS[datetime.time].from_string(time_part)
        return datetime.datetime.combine(the_date, the_time)

def add_converter(for_type, converter_instance):
    ''' Register a converter_instance to be used with for_type instances.
    The converter must implement from_string() and to_string(). '''
    if hasattr(converter_instance, 'from_string') and \
    hasattr(converter_instance, 'to_string'):
        _ALL_CONVERTERS[for_type] = converter_instance
        return
    msg = 'Converter for %s requires from_string() and to_string()' % for_type
    raise TypeError(msg)

# Register the standard converters for bool, int, float and datetime types
add_converter(bool, BoolConverter())
add_converter(int, FromConstructorConverter(int))
add_converter(float, FromConstructorConverter(float))
add_converter(datetime.date, DateConverter())
add_converter(datetime.time, TimeConverter())
add_converter(datetime.datetime, DatetimeConverter())

def convert_arg(to_type):
    ''' Method decorator to convert a slim-standard string arg to a specific
    python datatype "to_type". Delegates to from_string() method on a 
    type-specific Converter added through this module.'''
    def conversion_decorator(fn):
        ''' callable that performs the actual decoration '''
        converter = _ALL_CONVERTERS[to_type]
        return lambda self, value: fn(self, converter.from_string(value))
    return conversion_decorator

def convert_value(value):
    ''' Convert from a typed value to a string value with to_string().
    Try to use a registered type-specific converter if one exists,
    otherwise use the default (base Converter).''' 
    try:
        return _ALL_CONVERTERS[type(value)].to_string(value)
    except KeyError:
        return __DEFAULT_CONVERTER.to_string(value)