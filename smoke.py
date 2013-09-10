import converters
import execution
import fixtures
import instructions
import protocol
import server
import slim_exceptions
import smoke


class Options(object):
    inethost = '127.0.0.1'
    port = '8085'
    verbose = False

server.WaferSlimServer(Options())
