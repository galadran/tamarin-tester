#!/usr/bin/env python3

from argparse import ArgumentParser
from sys import exit 
from evaluate import run_evaluation
import config
import db

parser = ArgumentParser(description="TODO",add_help=True)

parser.add_argument("-v","--verbose",action='store_true',help="Run in verbose mode")
parser.add_argument("-d","--debug",action='store_true',help="Run in debug mode")
parser.add_argument("-s","--simple",action='store_true',\
                      help="Run with simple output, no colours or progress bars")
parser.add_argument("-db","--database",\
                      help="Specify an alternative database,"\
                      +" the default is stored in your user directory under ~/.config/tamarin-tester/results.db",\
                      default=config.DATABASE_PATH) #TODO Change

subparsers = parser.add_subparsers(help="Sub Commands",dest="mode",)

parser_eval = subparsers.add_parser('evaluate',\
                                help="Evaluate a Tamarin build against another on a specified set of protocols")
parser_eval.add_argument("test_binary",metavar='TEST_BINARY',\
                      help="This argument is the path to the Tamarin Binary you wish to evaluate against other Tamarin versions")
parser_eval.add_argument("test_protocols",metavar='TEST_PROTOCOLS',\
                      help="this argument is either a .spthy file, a directory containing .spthy files or a preprogrammed selection from the Tamarin examples."\
                      +" Options are fast,slow,all. Note that slow doesn't include fast, but slow+fast=all."\
                      +" Approximate running times are:....TODO") #TODO
parser_eval.add_argument("-r","--reference",\
                      help="This is either a path to a Tamarin binary or a Tamarin branch or a Tamarin commit to test against,"\
                      +" if ommitted, it defaults to the latest master commit",default="master",)
parser_eval.add_argument("-f","--failfast",action='store_true',\
                      help="Quit on the first error")
parser_eval.add_argument("-m","--max", metavar='FLOAT',\
                      help="Maximum time (in seconds) to run tests for, longer running tests will be skipped",type=float) 
parser_eval.add_argument("-p","--performance",action='store_true',\
                       help="This mode is stricter on performance requirments and will fail if performance differs.")

parser_hist = subparsers.add_parser('history',\
                                help="See the history of results for a set of protocols and tamarin versions")
#TODO Support Command

parser_ingest = subparsers.add_parser('ingest',\
                                help="Add new protocols to the protocol database")
#TODO Support Command

args = parser.parse_args()
config.VERBOSE = args.verbose
config.DEBUG = args.debug
config.DEBUG = True #TODO Remove when finished
config.SIMPLE = args.simple
config.DATABASE_PATH = args.database

db.openDatabase(config.DATABASE_PATH)

if args.mode == "evaluate":
  config.debug("Running evaluate subcommand")
  r = run_evaluation(args)
  config.debug("Finished running evaluate subcommand")
  exit(r)
elif args.mode == "history":
  #TODO
  config.warning("Not Yet Implemented!")
elif args.mode == "ingest":
  #TODO
  config.warning("Not Yet Implemented!")
else:
  config.fatalError("Unrecognised command - this should be unreachable")

config.fatalError("Dead code at the end of main.py, shouldn't be reachable")
