'''
BDD-style Lancelot specifications for the behaviour of the core library classes
'''

import lancelot

if __name__ == '__main__':
    from waferslim.specs import protocol_spec, execution_spec
    lancelot.verify()