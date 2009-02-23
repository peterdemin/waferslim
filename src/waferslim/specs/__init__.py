'''
WaferSlim specs (written using the lancelot BDD package).
    
The latest source code is available at http://code.launchpad.net/waferslim.

Copyright 2009 by the author(s). All rights reserved 
'''

import lancelot

if __name__ == '__main__':
    from waferslim.specs import protocol_spec, execution_spec
    lancelot.verify()