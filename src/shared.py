from blessings import Terminal
from glob import glob 
from hashlib import sha256
from datetime import timedelta

class Settings:
	def __init__(self, args):
		self.protocols = args.protocols  #Path to Protocl Directory
		self.tamarin = args.tamarin.name #Path to Tamarin Executable
		self.contingency = args.contingency #Max multiples of benchmark time to wait for
		self.repetitions = args.repetitions #How many samples to take for benchmark average
		self.verbose = args.verbose
		self.removeOvertime = args.overtime
		self.absolute = 0.0
		self.checkTime = 0.0
		self.input = ""
		self.output = ""
		if args.flags is not None:
			self.userFlags = args.flags #Any user defined flags to pass to Tamarin
		else:
			self.userFlags = ""
		
def prettyTime(s):
	return  str(timedelta(seconds=s)).split('.', 1)[0]
	
def validNormProtocol(tamarin,path,t):
	return tamarin.isWellFormed(path,0,t)

def validDiffProtocol(tamarin,path,t):
	return tamarin.isWellFormed(path,1,t)

def runAsDiff(tamarin,path,t):
	if validNormProtocol(tamarin,path,t) != 1 and validDiffProtocol(tamarin,path,t) == 1:
		return 1
	else:
		return 0	
		
def getProtocols(path):
		#Returns a list of strings holding each spthy file
		return glob(path+"/**/*.spthy",recursive=True)
		
def getUniqueProtocols(path):
	hashes = set()
	unique = list()
	ps = getProtocols(path)
	for p in ps:
		h = sha256(open(p,'rb').read()).hexdigest()
		if h in hashes:
			continue
		else:
			hashes.add(h)
			unique.append(p)
	duplicates = len(ps)-len(hashes)
	if duplicates > 0:
		print(INFORMATIONAL + "Ignoring "+ str(duplicates) + " duplicate protocols (identical hashes)")
	return unique		

		
VERSION = "Tamarin Tester v1.0.beta"
DESCRIPTION = "This program can be used to generate benchmark files for Tamarin which record correct results for a directory of protocols. Then it can be used to test an altered Tamarin compilation for correctness by comparing against these results. First navigate to a directory containing finished protocols and run Tamarin-Tester GOOD_TAMARIN_PATH. Then run Tamarin-Tester DEV_TAMARIN_PATH --b benchmark.txt and inspect the results."

TERMINAL = Terminal()

ERROR = TERMINAL.bold(TERMINAL.red("ERROR "))
INFORMATIONAL = TERMINAL.bold(TERMINAL.blue("INFORMATIONAL "))
WARNING = TERMINAL.yellow(TERMINAL.bold("WARNING "))

CHECK_TIMEOUT= TERMINAL.red(TERMINAL.bold("CHECK TIMEOUT "))
MALFORMED= TERMINAL.bold(TERMINAL.red("MALFORMED "))
BENCH_TIMEOUT= TERMINAL.red(TERMINAL.bold("BENCH TIMEOUT "))
NO_LEMMAS= TERMINAL.yellow(TERMINAL.bold("NO LEMMAS "))

INCORRECT= TERMINAL.bold(TERMINAL.red("\t INCORRECT: "))
STEPSIZE_INC= TERMINAL.bold(TERMINAL.yellow("\t STEPSIZE INC: "))
STEPSIZE_DEC= TERMINAL.bold(TERMINAL.yellow("\t STEPSIZE DEC: "))
TIMEOUT= TERMINAL.bold(TERMINAL.red("\t TIMEOUT "))

OVERTIME= TERMINAL.yellow(TERMINAL.bold("OVERTIME "))
MISSING= TERMINAL.yellow(TERMINAL.bold("MISSING "))
FAILED= TERMINAL.bold(TERMINAL.red("FAILED "))
PASSED= TERMINAL.bold(TERMINAL.green("PASSED "))