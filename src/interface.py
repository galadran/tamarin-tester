from subprocess import Popen, TimeoutExpired, CalledProcessError, PIPE
from sys import exit 
from os import devnull as os_devnull,killpg,setsid
from tqdm import tqdm
from signal import SIGINT
from hashlib import sha256

from shared import * 
from results import Result

class Tamarin:
	def __init__(self,config):
		self.path = config.tamarin
		self.flags = config.userFlags

	def getResults(self,protocol_path,diff,timeout):
		try:
			with open(os_devnull, 'w') as devnull:
				protFlags = extractFlags(protocol_path)
				allFlags = getFlags(self.flags,1, diff,protFlags)
				rawOutput = runWithTimeout(self.path+" "+allFlags+" "+ protocol_path,devnull,timeout)
				strOutput = str(rawOutput).replace("\\n","\n")
				if "TIMEOUT" not in strOutput: 
					strOutput = trimOutput(strOutput)
				return outputToResults(strOutput,protocol_path,diff,0.0,protFlags)
		except CalledProcessError:
					print(ERROR + " benchmarking " + protocol_path[len(paths):])
					exit(1)
		
	def isWellFormed(self,path,diff,timeout):
		#Tests whether a given protocol is well formed
		try:
			with open(os_devnull, 'w') as devnull:
				output = runWithTimeout(self.path+ getFlags(self.flags,0,diff,extractFlags(path)) +path,devnull,timeout)
			if " All well-formedness checks were successful." in str(output):
				return 1
			elif "TIMEOUT" in str(output):
				return -1
			else:
				return 0
		except CalledProcessError:
			return 0	
		
def getFlags(user,prove,diff,prot):
	#Build a flag string for Tamarin
	flags = user + " " + prot  
	if prove:
		flags += " --prove "
	if diff:
		flags += " --diff "
	return flags

def extractFlags(path):
	p = open(path,'r')
	rec = "#tamarin-tester-flags:"
	for line in p:
		if line[0:len(rec)] == rec:
			return line[len(rec):]
	return ""
	
def outputToResults(output, path, diff,avgTime,flags):
	#Create a results object out of TRIMMED Tamarin Output
	fileHash = sha256(open(path, 'rb').read()).hexdigest()
	if "TIMEOUT" in output:
		return Result(fileHash,diff,"TIMEOUT",0.0,flags)
	elif len(output) == 0:
		return Result(fileHash,diff,"NOLEMMAS",0.0,flags)
	return Result(fileHash,diff,extractLemmas(output),avgTime,flags)
	
def trimOutput(output):
	#Records all important lines between Summary of Summary and end of output
	reached = False
	filtered = ""
	for line in output.split('\n'):
		if reached and not line =="" and not"=" in line and not "'" in line and not '"' in line:
			if not len(filtered) == 0:
				filtered += "\n"
			filtered += line
		if "analyzed: " in line:
			reached = True
	return filtered
	
def extractLemmas(filtered):
	#Parses lemma lines into Records.
	try:
		lemmas = list()
		if "DiffLemma" in filtered:
			for line in filtered.split("\n"):
				state = "UNKNOWN"
				(side,name,b) = tuple(line.split(":"))
				(c,d) = tuple(b.split("("))
				if "falsified" in c:
					state = "FALSE"
				else:
					state = "TRUE"
				steps = ''.join(x for x in d if x.isdigit())
				lemmas.append((side+name,state,steps))
		else:
			for line in filtered.split("\n"):
				state = "UNKNOWN"
				(name,b) = tuple(line.split(":"))
				(c,d) = tuple(b.split("("))
				if "falsified" in c:
					state = "FALSE"
				else:
					state = "TRUE"
				steps = ''.join(x for x in d if x.isdigit())
				lemmas.append((name,state,steps))
		return lemmas
	except:
		print(ERROR + " failed to parse Tamarin output")
		print(filtered)
		exit(1)
		return "NONE"
			
def runWithTimeout(command,errOutput,time):
	#Run a command (INSECURE) with a specified timeout
	output = ""
	with Popen(command,shell=True,stdout=PIPE,stderr=errOutput,preexec_fn=setsid) as process:
		try:
			output = process.communicate(timeout=time)[0]
		except TimeoutExpired:
			killpg(process.pid, SIGINT)
			output = "TIMEOUT"
	return output