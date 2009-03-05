'''
BDD-style Lancelot specifications for the behaviour of the core library classes
'''

from waferslim.converters import register_converter, convert_value, \
    convert_arg, Converter, TrueFalseConverter, YesNoConverter, \
    FromConstructorConverter, DateConverter, TimeConverter, DatetimeConverter
import lancelot, datetime

class Fake(object):
    ''' Fake class whose str() value is determined by the constructor '''
    def __init__(self, str_value):
        ''' Specify value to return from str() '''
        self.str_value = str_value
    def __str__(self):
        ''' Return the specified str() value '''
        return self.str_value

@lancelot.verifiable
def base_converter_to_string():
    ''' Base Converter class should use str() as default implementation '''
    fake = Fake('Six bottles of Chateau Latour')
    spec = lancelot.Spec(Converter())
    spec.to_string(fake).should_be(fake.str_value)

@lancelot.verifiable
def base_converter_from_string():
    ''' Base Converter class should raise NotImplementedError '''
    spec = lancelot.Spec(Converter())
    spec.from_string('anything').should_raise(NotImplementedError)

@lancelot.verifiable
def convert_value_with_default_converter():
    ''' If no registered converter exists for the type of value being converted
    then the base Converter class should be used. '''
    fake = Fake('And a double Jeroboam of champagne')
    spec = lancelot.Spec(convert_value)
    spec.convert_value(fake).should_be(Converter().to_string(fake))
    
@lancelot.verifiable
def convert_value_with_registered_converter():
    ''' convert_value() should use the registered converter for the type
    of the value being converted if it exists. '''
    class FakeConverter(Converter, Fake):
        ''' Dummy Converter class, using Fake's constructor semantics'''
        def to_string(self, value):
            ''' Return str() value specified in constructor '''
            return self.str_value
    fake = Fake('I think I can only manage six crates today')
    converted_msg = 'I hope monsieur was not overdoing it last night'
    register_converter(Fake, FakeConverter(converted_msg))
    spec = lancelot.Spec(convert_value)
    spec.convert_value(fake).should_be(converted_msg)
    
@lancelot.verifiable
def register_converter_checks_attrs():
    ''' register_converter() will not accept a converter_instance without
    both to_string() and from_string() methods.'''
    converter = Fake("I'll have the lot")
    fake_method = lambda value: value
    spec = lancelot.Spec(register_converter)
    spec.register_converter(converter).should_raise(TypeError)

    converter.to_string = fake_method
    spec.register_converter(Fake, converter).should_raise(TypeError)

    del(converter.to_string)
    converter.from_string = fake_method
    spec.register_converter(Fake, converter).should_raise(TypeError)

    converter.to_string = fake_method
    converter.from_string = fake_method
    spec.register_converter(Fake, converter).should_not_raise(TypeError)
    
@lancelot.verifiable
def yesno_converter_behaviour():
    ''' YesNoConverter to_string() should be yes/no; from_string() should be
    True for any mixed case equivalent to yes; False otherwise. '''
    spec = lancelot.Spec(YesNoConverter())
    spec.to_string(True).should_be('yes')
    spec.to_string(False).should_be('no')
    spec.from_string('yes').should_be(True)
    spec.from_string('Yes').should_be(True)
    spec.from_string('True').should_be(False)
    spec.from_string('true').should_be(False)
    spec.from_string('no').should_be(False)
    spec.from_string('No').should_be(False)
    spec.from_string('false').should_be(False)
    spec.from_string('False').should_be(False)
    spec.from_string('jugged hare').should_be(False)
    
@lancelot.verifiable
def truefalse_converter_behaviour():
    ''' TrueFalseConverter to_string() should be true/false; from_string()  
    should be True for any mixed case equivalent to true; False otherwise. '''
    spec = lancelot.Spec(TrueFalseConverter())
    spec.to_string(True).should_be('true')
    spec.to_string(False).should_be('false')
    spec.from_string('yes').should_be(False)
    spec.from_string('Yes').should_be(False)
    spec.from_string('True').should_be(True)
    spec.from_string('true').should_be(True)
    spec.from_string('no').should_be(False)
    spec.from_string('No').should_be(False)
    spec.from_string('false').should_be(False)
    spec.from_string('False').should_be(False)
    spec.from_string('jugged hare').should_be(False)

@lancelot.verifiable
def from_constructor_conversion():
    ''' FromConstructorConverter converts using a type constructor, which
    is handy for int and float conversion '''
    spec = lancelot.Spec(FromConstructorConverter(int))
    spec.to_string(1).should_be('1')
    spec.to_string(2).should_be('2')
    spec.from_string('2').should_be(2)
    spec.from_string('1').should_be(1)
    
    spec = lancelot.Spec(FromConstructorConverter(float))
    spec.to_string(3.141).should_be('3.141')
    spec.from_string('3.141').should_be(3.141)

@lancelot.verifiable
def date_converter_behaviour():
    ''' DateConverter should convert to/from datetime.date type using 
    iso-standard format (4digityear-2digitmonth-2digitday)'''
    spec = lancelot.Spec(DateConverter())
    spec.to_string(datetime.date(2009,1,31)).should_be('2009-01-31')
    spec.from_string('2009-01-31').should_be(datetime.date(2009,1,31))
    
@lancelot.verifiable
def time_converter_behaviour():
    ''' TimeConverter should convert to/from datetime.date type using
    iso-standard format (2digithour:2digitminute:2digitsecond - with or without
    an additional optional .6digitmillis)'''
    spec = lancelot.Spec(TimeConverter())
    spec.to_string(datetime.time(1,2,3)).should_be('01:02:03')
    spec.to_string(datetime.time(1,2,3,4)).should_be('01:02:03.000004')
    spec.from_string('01:02:03').should_be(datetime.time(1,2,3))
    spec.from_string('01:02:03.000004').should_be(datetime.time(1,2,3,4))
    
@lancelot.verifiable
def datetime_converter_behaviour():
    ''' DatetimeConverter should convert to/from datetime.datetime type using
    combination of iso-standard formats ("dateformat<space>timeformat")'''
    spec = lancelot.Spec(DatetimeConverter())
    date_part, time_part = '2009-02-28', '21:54:32.987654'
    spec.to_string(datetime.datetime(2009,2,28,21,54,32,987654)).should_be(
        '2009-02-28 21:54:32.987654')
    spec.from_string('2009-02-28 21:54:32.987654').should_be(
        datetime.datetime.combine(DateConverter().from_string(date_part),
                                  TimeConverter().from_string(time_part))
        )
    
class ASystemUnderTest(object):
    ''' Dummy class with a setter method that can be decorated '''
    def set_afloat(self, float_value):
        ''' method to be decorated '''
        self.float_value = float_value

class ConvertArgBehaviour(object):
    ''' Group of related specs for convert_arg() behaviour.
    convert_arg() is a function decorator that should convert the single 
    arg supplied to the function into the required python type'''

    @lancelot.verifiable
    def returns_callable_to_type(self):
        ''' decorator for 'to_type' should return a callable that takes 2 args.
        Invoking that callable should convert the type of the 2nd arg.'''
        decorated_fn = convert_arg(to_type=float)(ASystemUnderTest.set_afloat)
        
        spec = lancelot.Spec(decorated_fn)
        spec.__call__('1.99').should_raise(TypeError) # only 1 arg
        
        sut = ASystemUnderTest()
        spec.__call__(sut, '1.99').should_not_raise(TypeError)
        
        spec.when(spec.__call__(sut, '2.718282'))
        spec.then(lambda: sut.float_value).should_be(2.718282)

    @lancelot.verifiable
    def returns_callable_using(self):
        ''' decorator for 'using' should return a callable that takes 2 args.
        Invoking that callable should convert the type of the 2nd arg.'''
        # Ensure that type-standard converter is not used!
        register_converter(float, Converter())
        
        cnvt = FromConstructorConverter(float)
        decorated_fn = convert_arg(using=cnvt)(ASystemUnderTest.set_afloat)
        
        spec = lancelot.Spec(decorated_fn)
        spec.__call__('1.99').should_raise(TypeError) # only 1 arg
        
        sut = ASystemUnderTest()
        spec.__call__(sut, '1.99').should_not_raise(TypeError)
        
        spec.when(spec.__call__(sut, '2.718282'))
        spec.then(lambda: sut.float_value).should_be(2.718282)
        
        # Reset type-standard converter
        register_converter(float, FromConstructorConverter(float))
                
    @lancelot.verifiable
    def fails_without_type_converter(self):
        ''' decorator should fail for to_type without a registered converter'''
        spec = lancelot.Spec(convert_arg(to_type=ASystemUnderTest))
        spec.__call__(lambda: None).should_raise(KeyError)

lancelot.grouping(ConvertArgBehaviour)

if __name__ == '__main__':
    lancelot.verify()
