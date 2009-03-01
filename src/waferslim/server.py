'''
Server classes. 

Run this module to start the WaferSlimServer listening on a host / port.
    
The latest source code is available at http://code.launchpad.net/waferslim.

Copyright 2009 by the author(s). All rights reserved 
'''
import logging, logging.config, SocketServer
from optparse import OptionParser
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
        
        server_address = (options.host, int(options.port))
        SocketServer.TCPServer.__init__(self, 
                                        server_address, SlimRequestHandler)
        
        start_msg = "Started and listening on %s:%s" % self.server_address
        logging.getLogger(_LOGGER_NAME).info(start_msg)
        
    def done(self, request_handler):
        ''' A request handler has completed: if keepalive=False then gracefully
        shut down the server'''
        if not self._keepalive:
            logging.getLogger(_LOGGER_NAME).info('Shutting down')
            self.shutdown()
            
    def _serve_until_shutdown(self):
        ''' Handle requests until shutdown is called '''
        while self._up: 
            self.handle_request()

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-p', '--port', dest='port', 
                      metavar='PORT', default=8989,
                      help='listen on port PORT')
    parser.add_option('-i', '--inet-host', dest='host', 
                      metavar='HOST', default='localhost',
                      help='listen on inet address HOST')
    parser.add_option('-v', '--verbose', dest='verbose', 
                      default=False,
                      help='log verbose messages at runtime')
    parser.add_option('-k', '--keep-alive', dest='keepalive', 
                      default=False,
                      help='keep the server alive to service multiple requests')
    parser.add_option('-l', '--logging-conf', dest='logconf', 
                      metavar='CONFIGFILE', default='logging.conf', 
                      help='get logging configuration from CONFIGFILE')
    (options, args) = parser.parse_args()

    logging.config.fileConfig(options.logconf)
    WaferSlimServer(options).serve_forever()
