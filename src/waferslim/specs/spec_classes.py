'''
Classes and functions for use in specs
'''

class ClassWithNoArgConstructor(object):
    ''' A class to instantiate with a no-arg constructor'''
    pass

class ClassWithOneArgConstructor(object):
    ''' A class to instantiate with a one-arg constructor'''
    def __init__(self, arg):
        pass

class ClassWithTwoArgConstructor(object):
    ''' A class to instantiate with a two-arg constructor'''
    def __init__(self, arg1, arg2):
        pass
