'''
Server classes. 

Run this module to start the WaferSlimServer listening on a host / port.
    
The latest source code is available at http://code.launchpad.net/waferslim.

Copyright 2009 by the author(s). All rights reserved 
'''
import logging, logging.config, SocketServer

from waferslim.protocol import RequestResponder

class SlimRequestHandler(SocketServer.BaseRequestHandler, RequestResponder):
    ''' Delegated the responsibility of handling TCP socket requests from
    the server -- in turn most of the work is passed off to the mixin class
    RequestResponder '''
      
    def handle(self):
        ''' log some info about the request then pass off to mixin class '''
        self._logger = logging.getLogger('WaferSlimServer')
        from_addr = '%s:%s' % self.client_address
        self.info('Handling request from %s' % from_addr)
        
        received, sent = self.respond_to_request()
        
        done_msg = 'Done with %s: %s bytes received, %s bytes sent'
        self.info(done_msg % (from_addr, received, sent))
        
    def info(self, msg):
        ''' log an info msg - present in this class to allow use from mixin'''
        self._logger.info(msg)
        
    def debug(self, msg):
        ''' log a debug msg - present in this class to allow use from mixin'''
        self._logger.debug(msg)

class WaferSlimServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    ''' Standard python library threaded TCP socket server __init__-ed 
    to delegate request handling to SlimRequestHandler ''' 
    
    def __init__(self, host, port):
        ''' Initialise socket server on host and port, with logging '''
        SocketServer.TCPServer.__init__(self, (host, port), SlimRequestHandler)
        start_msg = "Started and listening on %s:%s" % self.server_address
        logging.getLogger('WaferSlimServer').info(start_msg)

if __name__ == "__main__":
    #TODO: args: -p port, -v verbose
    port = 8989
    #TODO: more logging configuration
    logging.config.fileConfig('logging.conf')
    #TODO: graceful stop, start, restart, is-already-started
    WaferSlimServer('localhost', port).serve_forever()
