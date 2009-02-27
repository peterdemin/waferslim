'''
Simplistic classes and functions for use only in specs
'''

class ClassWithNoArgs(object):
    ''' A class to instantiate with a no-arg constructor'''
    pass

class ClassWithOneArg(object):
    ''' A class to instantiate with a one-arg constructor'''
    def __init__(self, arg):
        pass

class ClassWithTwoArgs(object):
    ''' A class to instantiate with a two-arg constructor'''
    def __init__(self, arg1, arg2):
        pass
