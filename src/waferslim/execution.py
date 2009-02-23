'''
Classes for turning instructions into a sequence of actions performed on 
the underlying system under test. 

The latest source code is available at http://code.launchpad.net/waferslim.

Copyright 2009 by the author(s). All rights reserved 
'''

class Instructions:
    def __init__(self, unpacked_list):
        ''' Specify the unpacked list containing instructions to execute '''
        pass
    
    def execute(self):
        ''' execute instructions one by one, and return a list of results '''
        return []