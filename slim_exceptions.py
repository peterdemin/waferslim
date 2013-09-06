class WaferSlimException(Exception):
    ''' Base Exception class for this package '''
    pass


class StopTestException(WaferSlimException):
    ''' Exception class to throw from fixtures that will stop test execution.
    See http://localhost:8080/FitNesse.UserGuide.SliM.ExceptionHandling '''
    pass
