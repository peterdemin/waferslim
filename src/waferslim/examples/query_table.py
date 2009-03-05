''' Example of a Slim QueryTable -- 
based on http://fitnesse.org/FitNesse.SliM.QueryTable'''

from waferslim.converters import convert_arg
import datetime

class EmployeesHiredBefore(object):
    ''' Class to be the system-under-test in fitnesse. '''

    @convert_arg(to_type=datetime.date)
    def __init__(self, before_date):
        ''' Specify the before_date for the query. 
        Method decorator ensures that arg passed in is datetime.date type.'''
        self._before_date = before_date
        
    def query(self):
        ''' Standard slim method for query tables. Returns a list of 
        lists of lists: each "row" of the query result is a list that contains
        a field-value list for each field value''' 
        return self._simulate_query(self._before_date)
    
    def _simulate_query(self, for_date_parameter):
        ''' Simulate performing a query e.g. on a database ''' 
        return [
                [
                ['employee number', '1429'],
                ['first name', 'Bob'],
                ['last name', 'Martin'],
                ['hire date', '1974-10-10'],
                ],
                [
                ['employee number', '8832'],
                ['first name', 'James'],
                ['last name', 'Grenning'],
                ['hire date', '1979-12-15'],
                ]
               ]
#TODO: Use People objects with conversion. List of str requires conversion with " not ' ! :-()