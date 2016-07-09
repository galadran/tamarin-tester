import glob
import re
from subprocess import Popen, TimeoutExpired, CalledProcessError, PIPE
import sys
import os
from blessings import Terminal
from tqdm import tqdm
import signal
import time
import datetime
import hashlib

term = Terminal()

class Parser:
	def __init__(self, config):
		self.config = config
		
	def getUniqueProtocols(self):
		hashes = set()
		unique = list()
		ps = self.getProtocols()
		for p in ps:
			h = hashlib.sha256(open(p,'rb').read()).hexdigest()
			if h in hashes:
				continue
			else:
				hashes.add(h)
				unique.append(p)
		duplicates = len(ps)-len(hashes)
		if duplicates > 0:
			print(term.bold(term.blue("INFORMATIONAL ")) + "Ignoring "+ str(duplicates) + " duplicate protocols (identical hashes)")
		return unique
		
	def getProtocols(self):
		#Returns a list of strings holding each spthy file
		return glob.glob(self.config.protocols+"/**/*.spthy",recursive=True)
		
	def getValidProtocols(self, protocols):
		#Given a list of protocols, check well-formedness of each
		tamarin_command = self.config.tamarin
		path = self.config.protocols
		validProtocols= list()
		skips = ""
		start = time.time()
		for p in tqdm(protocols,leave=False,smoothing=0.0,desc="Well Formedness Checks"):
			vp = self.validNormProtocol(p)
			vdp = self.validDiffProtocol(p)
			if vp !=1 and vdp != 1:
				if vp + vdp < 0:
					tqdm.write(term.red(term.bold("CHECK TIMEOUT ")) + p[len(path):])
				else:
					tqdm.write(term.red(term.bold("MALFORMED ")) + p[len(path):])
				continue
			else:
				validProtocols.append(p)
		td = time.time() - start
		print(term.bold(term.blue("INFORMATIONAL ")) + "Finished well-formedness checks in " + prettyTime(td))
		return validProtocols
		
	def validProtocol(self,path,diff):
		#Tests whether a given protocol is well formed
		try:
			with open(os.devnull, 'w') as devnull:
				output = runWithTimeout(self.config.tamarin+ getFlags(self.config.userFlags,0,diff,extractFlags(path)) +path,devnull,self.config.checkTime)
			if " All well-formedness checks were successful." in str(output):
				return 1
			elif "TIMEOUT" in str(output):
				return -1
			else:
				return 0
		except CalledProcessError:
			return 0

	def validNormProtocol(self,path):
		return self.validProtocol(path,0)
	
	def validDiffProtocol(self,path):
		#Tests whether a given protocol is valid with a diff flag
		return self.validProtocol(path,1)

	def runAsDiff(self,path):
		if self.validNormProtocol(path) != 1 and self.validDiffProtocol(path) == 1:
			return 1
		else:
			return 0		

def getFlags(userFlags,prove,diff,prot):
	#Build a flag string for Tamarin
	flags = userFlags + " " + prot  
	if prove:
		flags += " --prove "
	if diff:
		flags += " --diff "
	return flags

def prettyTime(s):
	return  str(datetime.timedelta(seconds=s)).split('.', 1)[0]

def extractFlags(path):
	p = open(path,'r')
	rec = "#tamarin-tester-flags:"
	for line in p:
		if line[0:len(rec)] == rec:
			return line[len(rec):]
	return ""
	
def runWithTimeout(command,errOutput,time):
		#Run a command (INSECURE) with a specified timeout
		output = ""
		with Popen(command,shell=True,stdout=PIPE,stderr=errOutput,preexec_fn=os.setsid) as process:
			try:
				output = process.communicate(timeout=time)[0]
			except TimeoutExpired:
				os.killpg(process.pid, signal.SIGINT)
				output = "TIMEOUT"
		return output

def getName(path):
	#Return the name of a protocol at a file
	with open(path, 'r') as f:
		for line in f:
			if re.match("^theory \w+", line):
				close(f)
				return line.split(' ')[1]
		exit(1)
		return("No defined name")


