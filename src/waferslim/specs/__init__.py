'''
BDD-style Lancelot specifications for the behaviour of the core library classes
'''

import lancelot

if __name__ == '__main__':
    from waferslim.specs import protocol_spec, instruction_spec, \
                                execution_spec, converter_spec, \
                                integration
    lancelot.verify()