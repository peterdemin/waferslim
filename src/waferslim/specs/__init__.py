'''
WaferSlim specs (written using the lancelot BDD package).
    
The latest source code is available at http://code.launchpad.net/waferslim.

Copyright 2009 by the author(s). All rights reserved 
'''

import lancelot

if __name__ == '__main__':
    import waferslim.specs.protocol_spec
    lancelot.verify()