'''
Example of how waferslim finds method names in fixtures

Fitnesse table markup:

|import|
|waferslim.examples.method_names|

|scenario|invoke|methodName|with|argValue|
|check|@methodName|@argValue|@argValue|

|script|class with pythonic method names|

|script|
|invoke|a method|with|hello world|
|invoke|a Method|with|hello World|
|invoke|A Method|with|Hello World|
|invoke|a_method|with|hello_world|
|invoke|aMethod|with|helloWorld|

|script|class with camel case method names|

|script|
|invoke|a method|with|hello world|
|invoke|a Method|with|hello World|
|invoke|A Method|with|Hello World|
|invoke|a_method|with|hello_world|
|invoke|aMethod|with|helloWorld|

Note that all the tests will pass for ClassWithPythonicMethodNames,
but "A Method" and "a_method" will fail for ClassWithCamelCaseMethodNames. 
'''
from waferslim.fixtures import EchoFixture

class ClassWithPythonicMethodNames(EchoFixture):
    ''' Simple class to show waferslim method matching ''' 
    def a_method(self, value):
        ''' A method with a pythonic name '''
        return self.echo(value)
    
class ClassWithCamelCaseMethodNames(EchoFixture):
    ''' Simple class to show waferslim method matching ''' 
    def aMethod(self, value):
        ''' A method with a camel cased name '''
        return self.echo(value)