import os
import collections
from . import converters
from . import execution
from . import fixtures
from . import instructions
from . import protocol
from . import server
from . import slim_exceptions


mute_unused_warnings = (converters, execution, fixtures, instructions,
                        protocol, server, slim_exceptions)

execution_context = execution.ExecutionContext()


def execute(instruction):
    execution_results = execution.Results()
    instruction.execute(execution_context, execution_results)
    return execution_results.collection()


Options = collections.namedtuple('Options', 'syspath inethost port verbose')
options = Options('fixtures', '127.0.0.1', '8085', False)
server._setup_syspath(options)
server.WaferSlimServer(options)

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
