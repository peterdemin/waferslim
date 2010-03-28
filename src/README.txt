################################
# DISCLAIMER AND LICENSE TERMS #
################################
This program is free software: you can redistribute it and/or modify it 
under the terms of the GNU Lesser General Public License as published by 
the Free Software Foundation, either version 3 of the License, or (at 
your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Lesser General Public License for more details.

You should have received a copy of the GNU General Public License and 
GNU Lesser General Public License along with this program.  If not, 
see <http://www.gnu.org/licenses/> 

#################################
# Installing waferslim          #
#################################
To install waferslim as a site-package run (from this directory) 

 python2 setup.py install 

For more information see http://docs.python.org/install/index.html#the-new-standard-distutils

#################################
# Using waferslim with fitnesse #
#################################
This release of waferslim has been tested with the fitnesse distribution 
20100103. Fitnesse distributions are available online at 
  http://fitnesse.org/FitNesseDevelopment.DownLoad
Fitnesse requires a Java Runtime Environment (JRE): Java 6 is recommended. 
If you are unfamiliar with fitnesse, the tutorials online (referenced at 
http://fitnesse.org) are recommended.

The fitnesse slim protocol allows tests to be specified in a language-neutral
format (HTML tables, edited through a wiki) and run using a language-specific
test runner: waferslim provides the hooks and plumbing for running fitnesse 
tests against a python code base.

Fitnesse communicates with waferslim using TCP sockets and needs to start an 
instance of the waferslim server each time a testable page ("test" or "suite") 
is run. To instruct fitnesse to use waferslim, your top-level wiki page 
needs to contain the following instructions:

  !define TEST_SYSTEM {slim} 
  !path /some/path/to/src
  !define COMMAND_PATTERN {python2 -m waferslim.server --syspath %p }

This tells fitnesse to use the slim protocol, and to start the waferslim server
using the sys.path listed in "!path". For multiple path entries, separate each 
path entry with the OS-specific path separator (the python os.pathsep value
i.e. ";" for windows, ":" otherwise).

Additional start-up parameters for the waferslim server can be specified in 
the COMMAND_PATTERN: 
     -h, --help                         see this list of options
     -p PORT, --port=PORT               listen on port PORT (see below)
     -i HOST, --inethost=HOST           listen on inet address HOST
                                        (default: localhost)
     -e ENCODING, --encoding=ENCODING   use byte-encoding ENCODING
                                        (default: utf-8)
     -v, --verbose                      log verbose messages at runtime
                                        (default: False)
     -k, --keepalive                    keep the server alive to service multiple
                                        requests, requires forked fitnesse code
                                        (default: False)
     -l FILE, --logconf=FILE            use logging configuration from FILE

Fitnesse itself supplies the port number by appending it to the end of the 
COMMAND_PATTERN: a "trailing" numeric value is assumed to be this port number
if none is specified explicitly, so the following are equivalent (though the
former is preferable):

    !define COMMAND_PATTERN {python -m waferslim.server --syspath %p }
    !define COMMAND_PATTERN {python -m waferslim.server --syspath %p --port }

########################################
# Executing python code from waferslim #
########################################

Fitnesse offers a variety of test table styles, all of which are supported by 
waferslim. Each table style causes waferslim to interact with the "system
under test" - your python code - in a slightly different way. Examples of
each of the table styles are provided in the sub-package waferslim.examples
which is intended as a useful reference guide (viewable online at
http://bazaar.launchpad.net/~prime8/waferslim/python25/files/head%3A/src/waferslim/examples) 

In broad terms waferslim interacts with the system under test as follows:
 - waferslim creates an instance of a class in your python code (an "import" 
   table in your fitnesse page helps waferslim to find and load the class)
 - waferslim invokes one or more methods on that class instance, (where the 
   method name is specified in the fitnesse table, usually in the column
   header), and values from the cells in the fitnesse table are passed as parameters
 - a return value from a method invocation is passed back to fitnesse which
   interprets it as a pass (green), fail (red) or error (yellow).

Because the fitnesse slim protocol is string-based, all method parameters
passed from fitnesse cells will be unicode strings (type "unicode") by default. 
The waferslim.converters module provides a method decorator to simplify the 
conversion of these parameters to native python types such as int, float, 
bool and datetime, e.g.

  from waferslim.converters import convert_arg
  ...
  class SomeClass:
      @convert_arg(to_type=int)
      def some_method(self, int_param)
          ...
      @convert_arg(to_type=(int, bool))
      def another_method(self, int_param, bool_param)
          ...

Method return values passed back to fitnesse must also be converted into strings
(again, unicode by default). This conversion should be transparent unless you 
have a class for which str(instance) does not provide the required conversion.

Converters for types not already handled by waferslim may be registered using
the register_converter function, e.g.:

  from waferslim.converters import register_converter
  ...
  register_converter(for_type, converter_instance)

The converter_instance is an object that has 2 specific methods:

  def from_string(self, value): ... # returns type-instance
  def to_string(self, value): ... # returns str-instance

You may wish to subclass the waferslim.converters.Converter class for your
own use.

An alternative to registering a custom converter (which will be used for all
the fitnesse test pages in a suite) is to use a "temporary" converter by
passing the named argument "using" to the @convert_arg and/or @convert_result
method decorators. This is recommended when using fitnesse decision tables
with the alternative boolean "Yes-No" converter, as with the example classes
in waferslim.examples.decision_table. (Registering the YesNoConverter in this
case would cause incorrect behaviour in any script tables run in the same
suite, as script tables require the default TrueFalseConverter to be used).
