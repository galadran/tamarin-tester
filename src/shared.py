import glob
import re
import subprocess
import sys
import os

def getProtocols(path):
	#Returns a list of strings holding each spthy file
	return glob.glob(path+"/**/*.spthy",recursive=True)


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

def loadBench(path):
	#Returns a list of benchmark results
	return 0
class Result: 
	def __init__(self,name,result,expectedTime,maxTime):
		self.name = name
		self.result = result
		self.expectedTime = expectedTime
		self.maxTime = maxTime

	def __str__(self):
		return str((self.name,self.result,self.expectedTime,self.maxTime))
