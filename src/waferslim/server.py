'''
Server classes. 

Run this module to start the WaferSlimServer listening on a host / port:

    Usage: 
        python -m waferslim.server [options]
    
    Options:
     -h, --help                see the full list of options
     -p PORT, --port=PORT      listen on port PORT
     -i HOST, --inethost=HOST  listen on inet address HOST
     -v, --verbose             log verbose messages at runtime
     -k, --keepalive           keep the server alive to service multiple
                               requests (requires fork of fitnesse java code)
     -l FILE, --logconf=FILE   get logging configuration from FILE
     -s PATH, --syspath=PATH   add ,-separated entries from PATH to sys.path
    When run from fitnesse the PORT argument must be specified last e.g.
    
    COMMAND_PATTERN {python -m waferslim.server --syspath %p --port} 
    
The latest source code is available at http://code.launchpad.net/waferslim.

Copyright 2009 by the author(s). All rights reserved 
'''
import logging, logging.config, SocketServer
from optparse import OptionParser
import os, sys
from waferslim.protocol import RequestResponder

_LOGGER_NAME = 'WaferSlimServer'
_ALL_LOGGER_NAMES = (_LOGGER_NAME, 'Instructions')

class SlimRequestHandler(SocketServer.BaseRequestHandler, RequestResponder):
    ''' Delegated the responsibility of handling TCP socket requests from
    the server -- in turn most of the work is passed off to the mixin class
    RequestResponder '''
      
    def handle(self):
        ''' log some info about the request then pass off to mixin class '''
        from_addr = '%s:%s' % self.client_address
        self.info('Handling request from %s' % from_addr)
        
        received, sent = self.respond_to_request()
        
        done_msg = 'Done with %s: %s bytes received, %s bytes sent'
        self.info(done_msg % (from_addr, received, sent))
        self.server.done(self)
        
    def info(self, msg):
        ''' log an info msg - present in this class to allow use from mixin'''
        logging.getLogger(_LOGGER_NAME).info(msg)
        
    def debug(self, msg):
        ''' log a debug msg - present in this class to allow use from mixin'''
        logging.getLogger(_LOGGER_NAME).debug(msg)

class WaferSlimServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    ''' Standard python library threaded TCP socket server __init__-ed 
    to delegate request handling to SlimRequestHandler ''' 
    
    def __init__(self, options):
        ''' Initialise socket server on host and port, with logging '''
        self._keepalive = options.keepalive
        if options.verbose:
            for name in _ALL_LOGGER_NAMES:
                logging.getLogger(name).setLevel(logging.DEBUG)
                
        if not hasattr(self, 'shutdown'): # only introduced in 2.6
            self._up = [True]
            self.shutdown = lambda: self._up and self._up.pop() or self._up
            self.serve_forever = self._serve_until_shutdown
        
        prestart_msg = "Starting server with options: %s" % options
        logging.getLogger(_LOGGER_NAME).info(prestart_msg)
        
        server_address = (options.inethost, int(options.port))
        SocketServer.TCPServer.__init__(self, 
                                        server_address, SlimRequestHandler)
        
        start_msg = "Started and listening on %s:%s" % self.server_address
        logging.getLogger(_LOGGER_NAME).info(start_msg)
        
    def done(self, request_handler):
        ''' A request_handler has completed: if keepalive=False then gracefully
        shut down the server'''
        if not self._keepalive:
            logging.getLogger(_LOGGER_NAME).info('Shutting down')
            self.shutdown()
            
    def _serve_until_shutdown(self):
        ''' Handle requests until shutdown is called '''
        if self._keepalive:
            while self._up:
                self.handle_request()
        else:
            self.handle_request()
            while self._up:
                pass

def _get_options():
    ''' Convenience method to parse command line args'''
    parser = OptionParser()
    parser.add_option('-p', '--port', dest='port', 
                      metavar='PORT', default=8989,
                      help='listen on port PORT')
    parser.add_option('-i', '--inethost', dest='inethost', 
                      metavar='HOST', default='localhost',
                      help='listen on inet address HOST')
    parser.add_option('-v', '--verbose', dest='verbose', 
                      default=False, action='store_true',
                      help='log verbose messages at runtime')
    parser.add_option('-k', '--keepalive', dest='keepalive', 
                      default=False, action='store_true',
                      help='keep the server alive - service multiple requests')
    parser.add_option('-l', '--logconf', dest='logconf', 
                      metavar='CONFIGFILE', default='', 
                      help='get logging configuration from CONFIGFILE')
    parser.add_option('-s', '--syspath', dest='syspath', 
                      metavar='SYSPATH', default='', 
                      help='add ,-separated entries from SYSPATH to sys.path')
    return parser.parse_args()

def start_server():
    ''' Convenience method to start the server (used by __main__)'''
    (options, args) = _get_options()
    
    if os.path.exists(options.logconf):
        logging.config.fileConfig(options.logconf)
    else:
        logging.basicConfig()
        if options.logconf:
            logging.warn('Invalid logging config file: %s' % options.logconf)
        
    for element in options.syspath.split(','):
        sys.path.append(element)
    
    WaferSlimServer(options).serve_forever()

if __name__ == '__main__':
    start_server()
