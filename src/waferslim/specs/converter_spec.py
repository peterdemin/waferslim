'''
BDD-style Lancelot specifications for the behaviour of the core library classes
'''

from waferslim.converters import add_converter, convert_value, convert_arg, \
                                 Converter, BoolConverter, \
                                 FromConstructorConverter
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
    add_converter(Fake, FakeConverter(converted_msg))
    spec = lancelot.Spec(convert_value)
    spec.convert_value(fake).should_be(converted_msg)
    
@lancelot.verifiable
def add_converter_checks_attrs():
    ''' add_converter() will not accept a converter_instance without
    both to_string() and from_string() methods.'''
    converter = Fake("I'll have the lot")
    fake_method = lambda value: value
    spec = lancelot.Spec(add_converter)
    spec.add_converter(converter).should_raise(TypeError)

    converter.to_string = fake_method
    spec.add_converter(Fake, converter).should_raise(TypeError)

    del(converter.to_string)
    converter.from_string = fake_method
    spec.add_converter(Fake, converter).should_raise(TypeError)

    converter.to_string = fake_method
    converter.from_string = fake_method
    spec.add_converter(Fake, converter).should_not_raise(TypeError)
    
@lancelot.verifiable
def bool_converter_behaviour():
    ''' BoolConverter to_string() should be yes/no; from_string should be
    True for any mixed case equivalent to yes or true; False otherwise. '''
    spec = lancelot.Spec(BoolConverter())
    spec.to_string(True).should_be('yes')
    spec.to_string(False).should_be('no')
    spec.from_string('yes').should_be(True)
    spec.from_string('Yes').should_be(True)
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

class SomeSystemUnderTest(object):
    ''' Dummy class with a setter method that can be decorated '''
    def set_afloat(self, float_value):
        ''' method to be decorated '''
        self.float_value = float_value

class ConvertArgBehaviour(object):
    ''' Group of related specs for convert_arg() behaviour.
    convert_arg() is a function decorator that should convert the single 
    arg supplied to the fuction into the required python type'''
            
    @lancelot.verifiable
    def returns_callable(self):
        ''' decorator should return a callable which takes 2 args.
        Invoking that callable should convert the type of the 2nd arg.'''
        decorated_fn = convert_arg(float)(SomeSystemUnderTest.set_afloat)
        
        spec = lancelot.Spec(decorated_fn)
        spec.__call__('1.99').should_raise(TypeError) # only 1 arg
        
        sut = SomeSystemUnderTest()
        spec.__call__(sut, '1.99').should_not_raise(TypeError)
        
        spec.when(spec.__call__(sut, '2.718282'))
        spec.then(lambda: sut.float_value).should_be(2.718282)
        
    @lancelot.verifiable
    def fails_without_type_converter(self):
        ''' decorator should fail for to_type without a registered converter'''
        spec = lancelot.Spec(convert_arg(to_type=SomeSystemUnderTest))
        spec.__call__(lambda: None).should_raise(KeyError)
        
lancelot.grouping(ConvertArgBehaviour)

if __name__ == '__main__':
    lancelot.verify()

