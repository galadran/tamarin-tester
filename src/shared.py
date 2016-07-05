import glob
import re
import subprocess
import sys
import os

def getProtocols(path):
	#Returns a list of strings holding each spthy file
	return glob.glob(path+"/**/*.spthy",recursive=True)

def getValidProtocols(tamarin_command,path):
	protocols = getProtocols(path)
	validProtocols= list()
	for p in protocols:
        	if not validateProtocol(tamarin_command,p) and not validDiffProtocol(tamarin_command,p):
                	print("Skipping " + p + " as well formedness check failed.")
                	continue
        	else:
                	validProtocols.append(p)
	print(str(len(validProtocols))+" out of "+str(len(protocols))+" protocols passed the checks.")
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
			output = subprocess.check_output(tamarin_command+" "+path,shell=True,stderr=devnull)
		if " All well-formedness checks were successful." in str(output):
			return 1
		else: 
			return 0
	except subprocess.CalledProcessError:
		return 0

def validDiffProtocol(tamarin_command,path):
	#Tests whether a given protocol is valid with a diff flag
	return validateProtocol(tamarin_command,"--diff "+path)

def runAsDiff(tamarin_command,path):
	if not validateProtocol(tamarin_command,path) and validDiffProtocol(tamarin_command,path):
		return 1
	else:
		return 0

