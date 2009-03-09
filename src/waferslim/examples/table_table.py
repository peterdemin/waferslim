''' Example of a Slim 'Table' Table -- 
based on http://fitnesse.org/FitNesse.SliM.TableTable.
This kind of table has to do all the calculation work for determining whether
an actual result for a cell is the same as the expected result, and passes
back cell-by-cell result values.
'''

_NO_CHANGE = '' # Leave the cell uncoloured
_CORRECT = 'pass' # Colour the cell green
_INCORRECT = '%s' # Colour the cell red and set its contents
_ERROR = 'error:%s' # Colour the cell yellow and set its contents

class Bowling(object):
    ''' Class to be the system-under-test in fitnesse. '''
    
    def doTable(self, table_rows):
        ''' Standard entry point for Slim Table Table. 
        table_rows is a tuple containing a tuple for each row in the 
        fitnesse table (in this case 1 row for rolls and 1 row for scores)'''
        return self._score_game(table_rows[0], table_rows[1])
        
    def _score_game(self, rolls, expected_scores):
        ''' Calculate the actual scores for each roll, and determine 
        how they differ from the expected scores '''
        actual_scores = []
        game = BowlingGame(actual_scores)
        for roll in rolls:
            game.roll(roll)
        score_differences = [self._differs(i, expected_scores, actual_scores) \
                             for i in range(0, len(expected_scores)) ]
        return [[_NO_CHANGE for roll in rolls], score_differences]
    
    def _differs(self, at_position, expected, actual):
        ''' Determine if expected and actual results at_position match''' 
        if expected[at_position] == actual[at_position]:
            return _CORRECT
        return _INCORRECT % actual[at_position]

class BowlingGame(object):
    ''' A bowling game -- scoring is not implemented ;-) '''
    _NO_PINS = '-'
    _STRIKE = 'X'
    _SPARE = '/'
    
    def __init__(self, score_holder):
        ''' Set up a new game with a list to act as score_holder''' 
        self._score_holder = score_holder
        
    def roll(self, outcome):
        ''' Roll a ball that knocks down some pins to produce the outcome '''
        self._score_holder.append('NOT IMPLEMENTED')
