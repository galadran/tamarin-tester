from shared import *
from bench import *
import argparse
import pathtype
import os

des = "This program will either test a Tamarin build against expected ones or else generated a standard set of results"

parser = argparse.ArgumentParser(description=des)
parser.add_argument("--protocols", help="directory containing test protocols", type=pathtype.PathType(exists=True, type='dir'),default=os.getcwd()+"/protocols")
parser.add_argument("--benchmark", help="file containing benchmark results", type=argparse.FileType('r'))
parser.add_argument("--tamarin", help="path to tamarin executable", type=argparse.FileType('r'))
parser.add_argument("--contingency", help="integer multiples of avg time to test for, defaults to 2", type=int,default=2)
parser.add_argument("--repitions", help="Number of iterations to benchmark for, defaults to 3",type=int,default = 3)
args = parser.parse_args()

if args.tamarin is not None:
	tamarin_command = args.tamarin.name
else:
	tamarin_command = "tamarin-prover"

protocols = getProtocols(args.protocols)
validProtocols= list()
for p in protocols:
	if not validateProtocol(tamarin_command,p) and not validDiffProtocol(tamarin_command,p):
		print("Skipping " + p + " as well formedness check failed.")
		continue
	else:
		validProtocols.append(p)

print(str(len(validProtocols))+" out of "+str(len(protocols))+" protocols passed the checks.")
