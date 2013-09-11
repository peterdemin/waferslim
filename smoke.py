import os
import sys
import collections
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from waferslim import converters
from waferslim import execution
from waferslim import fixtures
from waferslim import instructions
from waferslim import protocol
from waferslim import server
from waferslim import slim_exceptions


mute_unused_warnings = (converters, execution, fixtures, instructions,
                        protocol, server, slim_exceptions)

execution_context = execution.ExecutionContext()


def execute(instruction):
    execution_results = execution.Results()
    instruction.execute(execution_context, execution_results)
    return execution_results.collection()


class Options(object):
    inethost = '127.0.0.1'
    port = '8085'
    verbose = False

server._setup_syspath(collections.namedtuple('Options', 'syspath')('fixtures'))
server.WaferSlimServer(Options())

fixtures_path = os.path.join('echo_fixture.py')

assert execute(
    instructions.Import('import_0_0', [fixtures_path])
) == [['import_0_0', 'OK']]

assert execute(
    instructions.Make('make_0_0', ['echoer', 'EchoFixture'])
) == [['make_0_0', 'OK']]

assert execute(
    instructions.Call('call_0_0',
                      ['echoer', 'echo', 'hello'])
) == [['call_0_0', 'hello']]
