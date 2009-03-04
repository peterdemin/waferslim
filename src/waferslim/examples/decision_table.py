''' Example of a DecisionTable -- 
taken from http://fitnesse.org/FitNesse.SliM.DecisionTable'''

from waferslim.converters import convert_arg

class ShouldIBuyMilk:
    ''' Class to be the system-under-test in fitnesse. '''
    
    def __init__(self):
        ''' New instance has no cash, credit or pints of milk '''
        self._cash = 0
        self._credit = False
        self._pints = 0
        
    @convert_arg(to_type=int)
    def setCashInWallet(self, int_amount):
        ''' Decorated method to set cash as an int.
        The decorator translates from a standard slim string value. '''
        self._cash = int_amount
        
    @convert_arg(to_type=bool)
    def setCreditCard(self, bool_value):
        ''' Decorated method to set credit as a bool.
        The decorator translates from a standard slim string value. '''
        self._credit = bool_value
        
    @convert_arg(to_type=int)
    def setPintsOfMilkRemaining(self, int_amount):
        ''' Decorated method to set pints of milk as an int.
        The decorator translates from a standard slim string value. '''
        self._pints = int_amount
        
    def goToStore(self):
        ''' Return whether I should go to the store or not.
        The result will be translated to a standard slim string value
        without needing decoration, when invoked through waferslim. '''
        return self._pints == 0 and (self._credit or self._cash > 2)

class ShouldIBuyMilkAlternativeImplementation(ShouldIBuyMilk):
    ''' Alternative implementation of ShouldIBuyMilk to illustrate
    use of execute() and reset() methods. '''
    
    def __init__(self):
        ''' New instance will not go to store by default '''
        super().__init__()
        self._goToStore = False
        
    def goToStore(self):
        ''' Return whether I should go to the store or not, this time with
        the calculation done elsewhere.'''
        return self._goToStore
    
    def execute(self):
        ''' Slim-standard method that will be invoked after variables are set,
        if it exists ''' 
        if self._pints == 0 and (self._credit or self._cash > 2):
            self._goToStore = True
    
    def reset(self):
        ''' Slim-standard method that will be invoked before each table row, 
        if it exists ''' 
        self._goToStore = False
