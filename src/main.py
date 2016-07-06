from shared import *
from bench import *
from test import *
import argparse
import pathtype
import os
from blessings import Terminal
from settings import Settings

des = "This program will either test a Tamarin build against expected ones or else generated a standard set of results"

parser = argparse.ArgumentParser(description=des)
parser.add_argument("--protocols", help="directory containing test protocols", type=pathtype.PathType(exists=True, type='dir'),default=os.getcwd())
parser.add_argument("--benchmark", help="file containing benchmark results", type=argparse.FileType('r'))
parser.add_argument("tamarin", help="path to tamarin executable", type=argparse.FileType('r'))
parser.add_argument("--contingency", help="integer multiples of avg time to test for, defaults to 2", type=int,default=2)
parser.add_argument("--repitions", help="Number of iterations to benchmark for, defaults to 3",type=int,default = 3)
parser.add_argument("--max", help="Maximum time to run a proof for, defaults to 30 seconds",type=int,default=30)
parser.add_argument("--flags", help="User defined flags to pass to Tamarin for EVERY protocol",type=str)
args = parser.parse_args()

term = Terminal()

if len(getProtocols(args.protocols)) == 0:
	print(term.red("ERROR ")+ "No protocols found")
	exit(1)

if args.benchmark is None:
	print("Creating benchmark file")
	performBenchmark(Settings(args))
else:
	print("Testing against passed benchmark file")
	t = Tester(Settings(args))
	t.performTest()

