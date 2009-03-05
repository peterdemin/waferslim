''' Example of a Slim ScriptTable -- 
based on http://fitnesse.org/FitNesse.SliM.ScriptTable'''

from waferslim.converters import convert_arg, register_converter, \
                                 TrueFalseConverter

# At present, script tables require TrueFalseConverter 
register_converter(bool, TrueFalseConverter())

class LoginDialogDriver(object):
    ''' Class to be the system-under-test in fitnesse. '''
    
    def __init__(self, user_name, password):
        ''' New instance for the user_name and password specified has 0
        current login attempts and no message '''
        self._user_name = user_name
        self._password = password
        self._login_attempts = 0
        self._message = None
        
    def loginWithUsernameAndPassword(self, user_name, password):
        ''' Attempt to login with a user_name/ password combination. Fails
        unless args specified here match those specified in __init__.
        Note: no conversion-related decoration of this method is required 
        because the params are str-s and the return bool value is implicitly
        converted using the default TrueFalseConverter'''
        self._login_attempts += 1
        if self._user_name == user_name and self._password == password:
            self._message = '%s logged in.' % user_name
            return True
        self._message = '%s not logged in.' % user_name
        return False
    
    def loginMessage(self):
        ''' Expose the internals of the sut to check the login message.
        Note: no conversion-related decoration of this method is required 
        because there are no params and the return value is already a str'''
        return self._message

    def numberOfLoginAttempts(self):
        ''' Expose the internals of the sut to check number of login attempts.
        Note: no conversion-related decoration of this method is required 
        because there are no params and the numeric return value is 
        implicitly converted by a standard registered converter'''
        return self._login_attempts 
