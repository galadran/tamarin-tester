from shared import *
from bench import *
from test import *
import argparse
import pathtype
import os
from blessings import Terminal
from settings import Settings

des = "This program can be used to generate benchmark files for Tamarin which record correct results for a directory of protocols. Then it can be used to test an altered Tamarin compilation for correctness by comparing against these results. First navigate to a directory containing finished protocols and run Tamarin-Tester GOOD_TAMARIN_PATH. Then run Tamarin-Tester DEV_TAMARIN_PATH --b benchmark.txt and inspect the results."

parser = argparse.ArgumentParser(description=des)
parser.add_argument("-p","--protocols", metavar='DIR', help="directory containing test protocols", type=pathtype.PathType(exists=True, type='dir'),default=os.getcwd())
parser.add_argument("-b","--benchmark", metavar='FILE', help="file containing benchmark results", type=argparse.FileType('r'))
parser.add_argument("tamarin", metavar='FILE', help="path to tamarin executable", type=argparse.FileType('r'))
parser.add_argument("-c","--contingency", metavar='2', help="integer multiples of avg time to test for, defaults to 2", type=int,default=2)
parser.add_argument("-r","--repetitions", metavar='3', help="Number of iterations to benchmark for, defaults to 3",type=int,default = 3)
parser.add_argument("-m","--max", metavar='30',help="Maximum time to run a proof for, defaults to 30 seconds",type=int,default=30)
parser.add_argument("-f","--flags", metavar='FLAGS',help="User defined flags to pass to Tamarin for EVERY protocol",type=str)
parser.add_argument("-o","--output", metavar='benchmark.txt',help="Location of output file, defaults to local directory",type=pathtype.PathType(exists=False, type='file'))

args = parser.parse_args()

term = Terminal()

if len(getProtocols(args.protocols)) == 0:
	print(term.red("ERROR ")+ "No protocols found")
	exit(1)

if args.benchmark is None:
	print("Mode: Create Benchmark")
	b = Bencher(Settings(args))
	b.performBenchmark()
else:
	print("Mode: Comparing to Benchmark")
	t = Tester(Settings(args))
	t.performTest()
