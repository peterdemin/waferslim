import os
import collections
from waferslim import converters
from waferslim import execution
from waferslim import instructions
from waferslim import protocol
from waferslim import server
from waferslim import slim_exceptions


mute_unused_warnings = (converters, execution, instructions,
                        protocol, server, slim_exceptions)

execution_context = execution.ExecutionContext()


def execute(instruction):
    execution_results = execution.Results()
    instruction.execute(execution_context, execution_results)
    return execution_results.collection()


Options = collections.namedtuple('Options', 'syspath inethost port verbose')
options = Options(
    os.path.join(os.path.dirname(__file__), 'fixtures'),
    '127.0.0.1',
    '8085',
    False,
)
server._setup_syspath(options)
server.WaferSlimServer(options)


assert execute(
    instructions.Import('import_0_0', ['echo_fixture.py'])
) == [['import_0_0', 'OK']]

assert execute(
    instructions.Make('make_0_0', ['echoer', 'EchoFixture'])
) == [['make_0_0', 'OK']]

assert execute(
    instructions.Call('call_0_0',
                      ['echoer', 'echo', 'hello'])
) == [['call_0_0', 'hello']]
