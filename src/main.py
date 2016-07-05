from shared import *
from bench import *
from test import *
import argparse
import pathtype
import os

des = "This program will either test a Tamarin build against expected ones or else generated a standard set of results"

parser = argparse.ArgumentParser(description=des)
parser.add_argument("--protocols", help="directory containing test protocols", type=pathtype.PathType(exists=True, type='dir'),default=os.getcwd())
parser.add_argument("--benchmark", help="file containing benchmark results", type=argparse.FileType('r'))
parser.add_argument("tamarin", help="path to tamarin executable", type=argparse.FileType('r'))
parser.add_argument("--contingency", help="integer multiples of avg time to test for, defaults to 2", type=int,default=2)
parser.add_argument("--repitions", help="Number of iterations to benchmark for, defaults to 3",type=int,default = 3)
args = parser.parse_args()

if len(getProtocols(args.protocols)) == 0:
	print("No protocols found")
	exit(1)

if args.benchmark is None:
	print("Creating benchmark file")
	performBenchmark(args.tamarin.name,args.protocols,args.repitions)
else:
	print("Testing against passed benchmark file")
	performTest(args.tamarin.name,args.protocols,args.benchmark.name,args.contingency)
