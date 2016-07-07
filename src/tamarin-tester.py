from shared import *
from bench import *
from test import *
import argparse
import pathtype
import os
from blessings import Terminal
from settings import Settings

des = "This program can be used to generate benchmark files for Tamarin which record correct results for a directory of protocols. Then it can be used to test an altered Tamarin compilation for correctness by comparing against these results. First navigate to a directory containing finished protocols and run Tamarin-Tester GOOD_TAMARIN_PATH. Then run Tamarin-Tester DEV_TAMARIN_PATH --b benchmark.txt and inspect the results."


#TODO Make some of these exclusive / grouped!
parser = argparse.ArgumentParser(description=des)
parser.add_argument("-p","--protocols", metavar='DIR', help="directory containing test protocols", type=pathtype.PathType(exists=True, type='dir'),default=os.getcwd())
parser.add_argument("-b","--benchmark", metavar='FILE', help="file containing benchmark results", type=argparse.FileType('r'))
parser.add_argument("tamarin", metavar='FILE', help="path to tamarin executable", type=argparse.FileType('r'))
parser.add_argument("-c","--contingency", metavar='2', help="integer multiples of avg time to test for, defaults to 2", type=int,default=2)
parser.add_argument("-r","--repetitions", metavar='3', help="Number of iterations to benchmark for, defaults to 3",type=int,default = 3)
parser.add_argument("-mp","--maxproof", metavar='30',help="Maximum time to run a proof for, defaults to 30 seconds",type=int,default=30)
parser.add_argument("-f","--flags", metavar='FLAGS',help="User defined flags to pass to Tamarin for EVERY protocol",type=str)
parser.add_argument("-o","--output", metavar='benchmark.txt',help="Location of output file, defaults to local directory",type=pathtype.PathType(exists=False, type='file'))
parser.add_argument("-mc","--maxcheck", metavar='10', help="Maximum time to run well-formedness check for, defaults to 10 seconds",type=int,default=10)
parser.add_argument("-v","--verbose",help="Enabled verbose logging",action='store_true')

args = parser.parse_args()
term = Terminal()
config = Settings(args)

print(term.bold(term.blue("INFORMATIONAL ")) + "Tamarin Tester v0.3")
if config.verbose:
	print(term.bold(term.blue("INFORMATIONAL ")) + "Verbose Logging Enabled")

if args.benchmark is None:
	if config.verbose:
		print(term.bold(term.blue("INFORMATIONAL ")) + "Mode: Create Benchmark")
		print(term.bold(term.blue("INFORMATIONAL ")) + "Running Tamarin Executable: " + config.tamarin)	
		print(term.bold(term.blue("INFORMATIONAL ")) + "Benchmark Output Location: " + config.output)
		print(term.bold(term.blue("INFORMATIONAL ")) + "Benchmarking Protocols in: " + config.protocols)
		print(term.bold(term.blue("INFORMATIONAL ")) + "User flags: " + config.userFlags)
		print(term.bold(term.blue("INFORMATIONAL ")) + "Benchmark Repetitions: " + str(config.repetitions))
		print(term.bold(term.blue("INFORMATIONAL ")) + "Max Check Time: " + str(config.checkTime))
		print(term.bold(term.blue("INFORMATIONAL ")) + "Max Proof Time: " + str(config.absolute))
	b = Bencher(config)
	b.performBenchmark()
else:
	if config.verbose:
		print(term.bold(term.blue("INFORMATIONAL ")) + "Mode: Comparing to Benchmark")
		print(term.bold(term.blue("INFORMATIONAL ")) + "Testing Tamarin Executable: " + config.tamarin)	
		print(term.bold(term.blue("INFORMATIONAL ")) + "Benchmark Input Location: " + str(config.benchmark))
		print(term.bold(term.blue("INFORMATIONAL ")) + "Testing Protocols in: " + config.protocols)
		print(term.bold(term.blue("INFORMATIONAL ")) + "Contingency Factor: " + str(config.contingency))
		print(term.bold(term.blue("INFORMATIONAL ")) + "Max Proof Time: " + str(config.absolute))
		print(term.bold(term.blue("INFORMATIONAL ")) + "Max Check Time: " + str(config.checkTime))		
	t = Tester(config)
	t.checkOvertime()
	t.estTestTime()
	t.performTest()
