'''
Classes for turning instructions into a sequence of actions performed on 
the underlying system under test. 

The latest source code is available at http://code.launchpad.net/waferslim.

Copyright 2009 by the author(s). All rights reserved 
'''
from waferslim import WaferSlimException

class InstructionException(WaferSlimException):
    ''' Indicate an Instruction-related error ''' 
    pass

class Instruction(object):
    ''' Base class for instructions '''
    
    def __init__(self, id, params):
        ''' Specify the id of this instruction, and its params.
        Params must be a list. '''
        if not isinstance(params, list):
            raise InstructionException('%r is not a list' % params)
        self._id = id
        self._params = tuple(params)
        
    def execute(self):
        ''' Execute this instruction and return the results '''
#        raise InstructionException('Can only execute() a sub-class')
        pass

class Import(Instruction):
    ''' An "import <path>" instruction '''
    pass

class Make(Instruction):
    ''' A "make <instance>, <class>, <args>..." instruction '''
    pass

class Call(Instruction):
    ''' A "call <instance>,<function>,<args>..." instruction '''
    pass

class CallAndAssign(Instruction):
    ''' A "callAndAssign <symbol>, <instance>, <function>, <args>..." 
    instruction '''
    pass
