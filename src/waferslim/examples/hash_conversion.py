''' Example of using Slim Markup Hash syntax  -- 
based on http://fitnesse.org/FitNesse.UserGuide.MarkupHashTable

Fitnesse table markup:

|import|
|waferslim.examples.hash_conversion|

|DT:People| !{fname:bob, lname:martin, nname:unclebob} | !{fname:guido, lname:vanRossum, nname:!-BenevolentDictatorForLife-!} |
|Person|nickname?|
|!{fname:bob,lname:martin}|unclebob|
|!{fname:guido,lname:vanRossum}|!-BenevolentDictatorForLife-!|

|DT:People| !{fname:bob, lname:martin, nname:unclebob} | !{fname:guido, lname:vanRossum, nname:!-BenevolentDictatorForLife-!} |
|nickname|Person?|
|unclebob|bob martin|
|!-BenevolentDictatorForLife-!|guido vanRossum|

'''

from waferslim.converters import convert_arg

class People:
    ''' Simple class to find a person by fname/lname match or nickname '''
    @convert_arg(to_type=(dict,dict))
    def __init__(self, person1, person2):
        ''' Specify findable people ''' 
        self._people = []
        self._people.extend((person1, person2))
        
    @convert_arg(to_type=dict)
    def set_person(self, person):
        ''' Specify the person to look for by fname/lname '''
        self._current_person = person
    
    def nickname(self):
        ''' Find the nickname of the matching person '''
        for person in self._people:
            if person['lname'] == self._current_person['lname'] \
            and person['fname'] == self._current_person['fname']:
                return person['nname']
        raise KeyError('No person %s %s' % (self._current_person['fname'],
                                            self._current_person['lname']))
    
    def set_nickname(self, nickname):
        ''' Specify the person to look for by nickname '''
        self._current_nickname = nickname
    
    def person(self):
        ''' Find the fname/lname of the matching person '''
        for person in self._people:
            if person['nname'] == self._current_nickname:
                return '%s %s' % (person['fname'], person['lname'])
        msg = 'No person with nickname %s'
        raise KeyError(msg % (self._current_nickname))
