'''
BDD-style Lancelot specifications for the behaviour of the core library classes
'''

import lancelot
from waferslim.protocol import SlimProtocol, UnpackingError

SAMPLE_DATA = [
               ([],                 '[000000:]'),
               (['hello'],          '[000001:000005:hello:]'),
               (['hello','world'],  '[000002:000005:hello:000005:world:]'),
               ([['element']],      '[000001:000024:[000001:000007:element:]:]')
              ]

class PackBehaviour(object):
    ''' Group of specs for protocol pack() behaviour '''
    
    @lancelot.verifiable
    def items_length_item_format(self):
        ''' Encoding as described in fitnesse.slim.ListSerializer Javadoc:
        Format:  [iiiiii:llllll:item...]
        All lists (including lists within lists) begin with [ and end with ].  
        After the [ is the 6 digit number of items in the list followed by a :.
        Then comes each item which is composed of a 6 digit length a : and 
        then the value of the item followed by a :. '''
        spec = lancelot.Spec(SlimProtocol())
        for unpacked, packed in SAMPLE_DATA:
            spec.pack(unpacked).should_be(packed)
            
    @lancelot.verifiable
    def pack_non_strings(self):
        ''' Use str() co-ercion for encoding non-string values, except for
        None which encodes as "null" ''' 
        spec = lancelot.Spec(SlimProtocol())
        spec.pack([1]).should_be('[000001:000001:1:]')
        spec.pack([None]).should_be('[000001:000004:null:]') #TODO: check this?!

lancelot.grouping(PackBehaviour)

class UnpackBehaviour(object):
    ''' Group of specs for protocol unpack() behaviour '''
    
    @lancelot.verifiable
    def unpack_strings_only(self):
        ''' Unpacking a non-string should raise an error ''' 
        spec = lancelot.Spec(SlimProtocol())
        spec.unpack(None).should_raise(TypeError('None is not a string'))
        spec.unpack(1).should_raise(TypeError('1 is not a string'))
        spec.unpack([]).should_raise(TypeError('[] is not a string'))
        
    @lancelot.verifiable
    def require_square_brackets(self):
        ''' Unpacking a string without a leading square bracket, 
        or a string without an ending square bracket should raise an error ''' 
        spec = lancelot.Spec(SlimProtocol())
        spec.unpack('').should_raise(
            UnpackingError("'' has no leading '['"))
        spec.unpack('[hello').should_raise(
            UnpackingError("'[hello' has no trailing ']'"))
        spec.unpack('hello]').should_raise(
            UnpackingError("'hello]' has no leading '['"))
        
    @lancelot.verifiable
    def items_length_item_format(self):
        ''' Unpacking should reverse the encoding process '''
        spec = lancelot.Spec(SlimProtocol())
        for unpacked, packed in SAMPLE_DATA:
            spec.unpack(packed).should_be(unpacked)

lancelot.grouping(UnpackBehaviour)

if __name__ == '__main__':
    lancelot.verify()