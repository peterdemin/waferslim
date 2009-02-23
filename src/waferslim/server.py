'''
Server classes. 

Run this module to start the WaferSlimServer listening on a host / port.
    
The latest source code is available at http://code.launchpad.net/waferslim.

Copyright 2009 by the author(s). All rights reserved 
'''
import logging, SocketServer

from waferslim.protocol import RequestResponder

class SlimRequestHandler(SocketServer.BaseRequestHandler, RequestResponder):
    ''' Delegated the responsibility of handling TCP socket requests from
    the server -- in turn most of the work is passed off to the mixin class
    RequestResponder '''
      
    def handle(self):
        ''' log some info about the request then pass off to mixin class '''
        from_addr = self.client_address
        self.info('Handling request from %s:%s' % from_addr)
        
        received, sent = self.respond_to(self.request)
        
        done_msg = 'Done: %s bytes received, %s bytes sent'
        self.info(done_msg % (received, sent))
        
    def info(self, msg):
        ''' log an info msg - present in this class to allow use from mixin'''
        logging.info(msg)
        
    def debug(self, msg):
        ''' log a debug msg - present in this class to allow use from mixin'''
        logging.debug(msg)

class WaferSlimServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    ''' Standard python library threaded TCP socket server __init__-ed 
    to delegate request handling to SlimRequestHandler ''' 
    
    def __init__(self, host, port):
        SocketServer.TCPServer.__init__(self, (host, port), SlimRequestHandler)
        logging.info("WaferSlimServer started on %s:%s" % self.server_address)

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)
    WaferSlimServer('localhost', 8989).serve_forever()
