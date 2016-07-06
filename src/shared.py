import glob
import re
from subprocess import Popen, TimeoutExpired, CalledProcessError, PIPE
import sys
import os
from blessings import Terminal
from tqdm import tqdm
import signal

term = Terminal()

def getFlags(userFlags, diff):
	flags = userFlags + " --prove "
	if diff:
		flags += "--diff "
	return flags

def runWithTimeout(command,errOutput,time):
		output = ""
		with Popen(command,shell=True,stdout=PIPE,stderr=errOutput,preexec_fn=os.setsid) as process:
			try:
				output = process.communicate(timeout=time)[0]
			except TimeoutExpired:
				os.killpg(process.pid, signal.SIGINT)
				output = "TIMEOUT"
		return output

def getProtocols(path):
	#Returns a list of strings holding each spthy file
	return glob.glob(path+"/**/*.spthy",recursive=True)

def getValidProtocols(tamarin_command,path):
	protocols = getProtocols(path)
	validProtocols= list()
	skips = ""
	for p in tqdm(protocols,leave=False):
		vp = validateProtocol(tamarin_command,p) 
		vdp = validDiffProtocol(tamarin_command,p)
		if vp !=1 and vdp != 1:
			if vp + vdp == -2:
				skips += (term.yellow(term.bold("TIMEOUT ")) + p[len(path):] + " \n")
			else:
				skips += (term.yellow(term.bold("INCORRECT ")) + p[len(path):] + " \n")
			continue
		else:
			validProtocols.append(p)
	if len(validProtocols) == len(protocols):
		print(term.green(str(len(validProtocols))+" out of "+str(len(protocols))+" protocols passed the well formedness checks."))
	elif 0 < len(validProtocols) and len(validProtocols) < len(protocols):
		print(term.yellow(str(len(validProtocols))+" out of "+str(len(protocols))+" protocols passed the well formedness checks."))
		print(skips,end="")
	elif len(validProtocols) == 0:
		print(term.red(str(len(validProtocols))+" out of "+str(len(protocols))+" protocols passed the well formedness checks."))
	return validProtocols


def getName(path):
	#Return the name of a protocol at a file
	with open(path, 'r') as f:
		for line in f:
			if re.match("^theory \w+", line):
				close(f)
				return line.split(' ')[1]
		exit(1)
		return("No defined name")

def validateProtocol(tamarin_command,path):
	#Tests whether a given protocol is well formed
	try:
		with open(os.devnull, 'w') as devnull:
			output = runWithTimeout(tamarin_command+" "+path,devnull,1)
		if " All well-formedness checks were successful." in str(output):
			return 1
		elif "TIMEOUT" in str(output):
			return -1
		else: 
			return 0
	except CalledProcessError:
		return 0

def validDiffProtocol(tamarin_command,path):
	#Tests whether a given protocol is valid with a diff flag
	return validateProtocol(tamarin_command,"--diff "+path)

def runAsDiff(tamarin_command,path):
	if validateProtocol(tamarin_command,path) != 1 and validDiffProtocol(tamarin_command,path) == 1:
		return 1
	else:
		return 0

