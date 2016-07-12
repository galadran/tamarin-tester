from tqdm import tqdm
from time import time
from hashlib import sha256

from shared import *
from results import fileToResults,compareResults
from interface import Tamarin


class Tester:
	def __init__(self, config):
		self.config = config
	
		self.tamarin = Tamarin(config)
		
		#Load protocols and benchmarks
		self.hashToPath = dict()
		ps = getUniqueProtocols(self.config.protocols)
		for p in ps:
			h = sha256(open(p,'rb').read()).hexdigest()
			self.hashToPath[h] = p
			
		self.flags, self.benchmarks = fileToResults(config.input)
		
		if config.absolute == 0.0:
			maxTime = 0.0
			for b in self.benchmarks :
				if b.fileHash in self.hashToPath.keys():
					maxTime = max(maxTime,b.avgTime)
			config.absolute = maxTime*config.contingency
			if self.config.verbose:
				print(INFORMATIONAL + "Loaded default max proof time from file " + prettyTime(config.checkTime))
		elif self.config.verbose:
			print(INFORMATIONAL + "Max Proof Time (from argument): " + prettyTime(config.absolute))
			
		if config.checkTime == 0.0:
			maxTime = 0.0
			for b in self.benchmarks:
				if b.fileHash in self.hashToPath.keys():
					maxTime = max(maxTime,b.avgTime)
			config.checkTime = min(maxTime,config.absolute)
			if self.config.verbose:
				print(INFORMATIONAL + "Used default max check time: (min(prooftime, maxFileTime)) " + prettyTime(config.checkTime))
		elif self.config.verbose:
			print(INFORMATIONAL + "Max Check Time (from argument): " + prettyTime(config.checkTime))
			
		#Reload the parser in case we made any changes
		self.config = config
		
		#Counters for results
		self.failures = 0
		self.passed = 0
		self.warning = 0
		self.missing = 0
		self.nolemmas = 0
		self.total = len(self.hashToPath.keys())
		self.removedOvertime = 0
		self.wereOvertime = list()
	
	def filterOvertime(self):
		orig = len(self.benchmarks)
		filtered = list()
		for b in self.benchmarks:
			if b.avgTime <= self.config.absolute:
				filtered.append(b)
			else:
				self.wereOvertime.append(b.fileHash)
		self.benchmarks = filtered
		self.removedOvertime = len(self.wereOvertime)
		print(INFORMATIONAL + "Removed " + str(self.removedOvertime) 
				+ " overtime protocols")		
	
	def checkOvertime(self):
		goingOvertime = 0
		maxSeen = 0.0
		for b in sorted(self.benchmarks, key=lambda bench: bench.avgTime):
			if b.fileHash in self.hashToPath.keys() and b.avgTime > self.config.absolute:
					goingOvertime += 1 
					maxSeen = max(maxSeen, b.avgTime)
		if goingOvertime > 0:
			if not self.config.removeOvertime:
				print(WARNING + str(goingOvertime) + " protocol(s) are not expected to terminate proving because the max proof time " + prettyTime(self.config.absolute) + " is less than their expected run time (Highest seen: " + prettyTime(maxSeen) + ")")
			return 1
		else:
			return 0
			
	def estTestTime(self):
		totalTime = 0.0
		for b in sorted(self.benchmarks, key=lambda bench: bench.avgTime):
			if b.fileHash in self.hashToPath.keys():
				totalTime += min(b.avgTime,self.config.absolute) 
		print(INFORMATIONAL + "Expected Test runtime is at least " + prettyTime(totalTime))
	
	def ignoreBench(self, b):
		#Returns 1 if a benchmark should be ignored, 0 otherwise
		if "TIMEOUT" in b.lemmas and b.avgTime > config.absolute:
			return 1
		else:
			return 0

	def performTest(self):
		#Runs tests and compares them against benchmarks
		config = self.config
		#Protocols are removed from this set as they found in the benchmark
		hashes = set(self.hashToPath.keys())
		#For each benchmark, sorted from quickest to slowest
		print(INFORMATIONAL +"Testing protocols...")
		start = time()
		for b in tqdm(sorted(self.benchmarks, key=lambda bench: bench.avgTime),smoothing=1.0,leave=False,desc="Testing against benchmarks"):
			if b.fileHash not in hashes or "TIMEOUT" in b.lemmas:
				#We can ignore this benchmark as either we have no data or its not in our test input
				continue
			hashes.remove(b.fileHash)
			#NoLemmas means that the benchmark had nothing to prove and hence we cannot test here
			if "NOLEMMAS" in b.lemmas:
				self.nolemmas += 1
				tqdm.write(NO_LEMMAS + self.hashToPath[b.fileHash][len(config.protocols):])
				continue
			#Here we check for well formedness
			if (not b.diff and validNormProtocol(self.tamarin,self.hashToPath[b.fileHash],self.config.checkTime)) or (b.diff and validDiffProtocol(self.tamarin,self.hashToPath[b.fileHash],self.config.checkTime)):
					tqdm.write(self.testProtocol(self.hashToPath[b.fileHash],b),end="")
			else:
				#Both test and benchmark versions should agree on well formedness
				tqdm.write(FAILED + self.hashToPath[b.fileHash][len(config.protocols):] + "\n" + MALFORMED + " should pass well-formedness check")
				self.failures+= 1
		#Print out protocols we could not find a benchmark for
		missing = list()
		for h in hashes:
			if h in self.wereOvertime:
				print(OVERTIME+ self.hashToPath[h][len(config.protocols):])
			else:
				self.missing+= 1
				missing.append(self.hashToPath[h][len(config.protocols):])
		for m in sorted(missing, key=str.lower):
		    print(NO_BENCHMARK + m)
		td = time() - start
		print(INFORMATIONAL + "Finished testing in " + prettyTime(td))
		self.printSummary()

	def printSummary(self):
		#'Pretty Print' a summary based on our counters
		print("=====================================")
		print("============== " + TERMINAL.bold("Summary") + " ==============")
		print("=====================================")

		print(TERMINAL.bold("TOTAL: " + str(self.total)))
		if self.failures != 0:
			print(TERMINAL.bold(TERMINAL.red("FAILED: " + str(self.failures))))
		if self.missing != 0:
			print(TERMINAL.bold(TERMINAL.yellow(NO_BENCHMARK + str(self.missing))))
		if self.removedOvertime != 0:
			print(TERMINAL.bold(TERMINAL.yellow("OVERTIME: " + str(self.removedOvertime))))			
		if self.nolemmas != 0:
			print(TERMINAL.bold(TERMINAL.yellow("NOLEMMAS: " + str(self.nolemmas))))
		if self.warning != 0:
			print(TERMINAL.bold(TERMINAL.yellow("WARNING: " + str(self.warning))))
		if self.passed != 0:
			print(TERMINAL.bold(TERMINAL.green("PASSED: " + str(self.passed))))
		if self.failures > 0:
			print("=====================================")
			print("=============== " + TERMINAL.red(TERMINAL.bold("FAIL")) + " ================")
			print("=====================================")
		elif self.warning + self.missing + self.nolemmas + self.removedOvertime > 0:
			print("=====================================")
			print("=============== " + TERMINAL.yellow(TERMINAL.bold("WARN")) + " ================")
			print("=====================================")
		else:
			print("=====================================")
			print("=============== " + TERMINAL.green(TERMINAL.bold("PASS")) + " ================")
			print("=====================================")

	def testProtocol(self,protocol_path,bench):
		#Given a specific protocol path and a benchmark result, test it
		config = self.config
		message = ""
		#We stop Tamarin when we go over our absolute or relative maximum
		allowedTime = min(config.absolute,bench.avgTime*config.contingency)
		output = self.tamarin.getResults(protocol_path,bench.diff,allowedTime)
		#If we TIMEOUT here, the benchmark did not and hence this is a failure
		if "TIMEOUT" in output.lemmas:
			self.failures+= 1
			ret = FAILED + protocol_path[len(config.protocols):] + "\n" + TIMEOUT + "after " + prettyTime(allowedTime) + " expected: " + prettyTime(bench.avgTime) +" \n"
			if bench.avgTime > self.config.absolute:
				return  ret + INFORMATIONAL + "this protocol was expected to timeout \n"
			else:
				return ret
		message = compareResults(output,bench)
		#Add a title message to our sublistings
		if "INCORRECT" in message:
			self.failures+= 1
			return FAILED + protocol_path[len(config.protocols):] + "\n" + message
		elif "STEPSIZE" in message:
			self.warning+= 1
			return WARNING + protocol_path[len(config.protocols):] + "\n" + message
		else:
			self.passed+= 1
			return PASSED + protocol_path[len(config.protocols):] + "\n" + message
