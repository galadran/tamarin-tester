from shared import *
from bench import *
from blessings import Terminal
from results import *
from tqdm import tqdm
import time
term = Terminal()

class Tester:
	def __init__(self, config):
		self.config = config
		
		self.parser = Parser(config)
		
		
		#Load protocols and benchmarks
		self.hashToPath = dict()
		for p in self.parser.getProtocols():
			self.hashToPath[hashlib.sha256(open(p,'rb').read()).hexdigest()] = p
		self.flags, self.benchmarks = fileToResults(config.benchmark)
		
		if config.absolute == 0.0:
			maxTime = 0.0
			for b in self.benchmarks:
				maxTime = max(maxTime,b.avgTime)
			config.absolute = maxTime*config.contingency
			if self.config.verbose:
				print(term.bold(term.blue("INFORMATIONAL ")) + "Loaded default max proof time from file " + prettyTime(config.checkTime))
		elif self.config.verbose:
			print(term.bold(term.blue("INFORMATIONAL ")) + "Max Proof Time (from argument): " + prettyTime(config.absolute))
			
		if config.checkTime == 0.0:
			maxTime = 0.0
			for b in self.benchmarks:
				maxTime = max(maxTime,b.avgTime)
			config.checkTime = min(maxTime,config.absolute)
			if self.config.verbose:
				print(term.bold(term.blue("INFORMATIONAL ")) + "Used default max check time: (min(prooftime, maxFileTime)) " + prettyTime(config.checkTime))
		elif self.config.verbose:
			print(str(self.config.checkTime))
			print(term.bold(term.blue("INFORMATIONAL ")) + "Max Check Time (from argument): " + prettyTime(config.checkTime))
			
		#Reload the parser in case we made any changes
		self.config = config
		self.parser = Parser(config)
		
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
		print(term.bold(term.blue("INFORMATIONAL ")) + "Removed " + str(self.removedOvertime) 
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
				print(term.bold(term.yellow("WARNING ")) + str(goingOvertime) + " protocol(s) are not expected to terminate proving because the max proof time " + prettyTime(self.config.absolute) + " is less than their expected run time (Highest seen: " + prettyTime(maxSeen) + ")")
			return 1
		else:
			return 0
			
	def estTestTime(self):
		totalTime = 0.0
		for b in sorted(self.benchmarks, key=lambda bench: bench.avgTime):
			if b.fileHash in self.hashToPath.keys():
				totalTime += min(b.avgTime*self.config.contingency,self.config.absolute) 
		print(term.bold(term.blue("INFORMATIONAL ")) + "Expected Test runtime is at least " + prettyTime(totalTime))
	
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
		print(term.bold(term.blue("INFORMATIONAL ")) +"Testing protocols...")
		start = time.time()
		for b in tqdm(sorted(self.benchmarks, key=lambda bench: bench.avgTime),smoothing=1.0,leave=False,desc="Testing against benchmarks"):
			if b.fileHash not in hashes or "TIMEOUT" in b.lemmas:
				#We can ignore this benchmark as either we have no data or its not in our test input
				continue
			hashes.remove(b.fileHash)
			#NoLemmas means that the benchmark had nothing to prove and hence we cannot test here
			if "NOLEMMAS" in b.lemmas:
				self.nolemmas += 1
				tqdm.write(term.bold(term.yellow("NO LEMMAS ")) + self.hashToPath[b.fileHash][len(config.protocols):])
				continue
			#Here we check for well formedness
			if (not b.diff and self.parser.validNormProtocol(self.hashToPath[b.fileHash])) or (b.diff and self.parser.validDiffProtocol(self.hashToPath[b.fileHash])):
					tqdm.write(self.testProtocol(self.hashToPath[b.fileHash],b),end="")
			else:
				#Both test and benchmark versions should agree on well formedness
				tqdm.write(term.bold(term.red("FAILED ")) + self.hashToPath[b.fileHash][len(config.protocols):] + "\n" + term.red("\t MALFORMED") + " should pass well-formedness check")
				self.failures+= 1
		#Print out protocols we could not find a benchmark for
		for h in hashes:
			if h in self.wereOvertime:
				print(term.yellow(term.bold("OVERTIME "))+ self.hashToPath[h][len(config.protocols):])
			else:
				self.missing+= 1
				print(term.yellow(term.bold("MISSING "))+ self.hashToPath[h][len(config.protocols):])
		td = time.time() - start
		print(term.bold(term.blue("INFORMATIONAL ")) + "Finished testing in " + prettyTime(td))
		self.printSummary()

	def printSummary(self):
		#'Pretty Print' a summary based on our counters
		print("=====================================")
		print("============== " + term.bold("Summary") + " ==============")
		print("=====================================")

		print(term.bold("TOTAL: " + str(self.total)))
		if self.failures != 0:
			print(term.bold(term.red("FAILED: " + str(self.failures))))
		if self.missing != 0:
			print(term.bold(term.yellow("MISSED: " + str(self.missing))))
		if self.removedOvertime != 0:
			print(term.bold(term.yellow("OVERTIME: " + str(self.removedOvertime))))			
		if self.nolemmas != 0:
			print(term.bold(term.yellow("NOLEMMAS: " + str(self.nolemmas))))
		if self.warning != 0:
			print(term.bold(term.yellow("WARNING: " + str(self.warning))))
		if self.passed != 0:
			print(term.bold(term.green("PASSED: " + str(self.passed))))
		if self.failures > 0:
			print("=====================================")
			print("=============== " + term.red(term.bold("FAIL")) + " ================")
			print("=====================================")
		elif self.warning + self.missing + self.nolemmas + self.removedOvertime > 0:
			print("=====================================")
			print("=============== " + term.yellow(term.bold("????")) + " ================")
			print("=====================================")
		else:
			print("=====================================")
			print("=============== " + term.green(term.bold("PASS")) + " ================")
			print("=====================================")

	def testProtocol(self,protocol_path,bench):
		#Given a specific protocol path and a benchmark result, test it
		config = self.config
		message = ""
		#We stop Tamarin when we go over our absolute or relative maximum
		allowedTime = min(config.absolute,bench.avgTime*config.contingency)
		try:
			#Ignore Tamarin Error messages (they will be unhelpful and misleading for us)
			with open(os.devnull, 'w') as devnull:
				#Launch the Tamarin instance
				output = runWithTimeout(config.tamarin+" "+getFlags(self.flags,bench.diff,extractFlags(protocol_path))+" "+ protocol_path,devnull,allowedTime)
				#If we TIMEOUT here, the benchmark did not and hence this is a failure
				if "TIMEOUT" in str(output):
					self.failures+= 1
					ret = term.bold(term.red("FAILED ")) + protocol_path[len(config.protocols):] + "\n" + term.bold(term.red("\t TIMEOUT ")) + "after " + prettyTime(allowedTime) + " expected: " + prettyTime(bench.avgTime) +" \n"
					if bench.avgTime > self.config.absolute:
						return  ret + term.bold(term.blue("\t INFORMATIONAL ")) + "this protocol was expected to timeout \n"
					else:
						return ret
		except CalledProcessError:
			#This indicates Tamarin raised an error. We output the file we had a problem with
			print(term.red("ERROR") + " Testing " + protocol_path[len(config.protocols):])
			exit(1)
		message = compareResults(extractLemmas(trimOutput(str(output).replace("\\n","\n"))),bench)
		#Add a title message to our sublistings
		if "INCORRECT" in message:
			self.failures+= 1
			return term.bold(term.red("FAILED ")) + protocol_path[len(config.protocols):] + "\n" + message
		elif "STEPSIZE" in message:
			self.warning+= 1
			return term.bold(term.yellow("WARNING ")) + protocol_path[len(config.protocols):] + "\n" + message
		else:
			self.passed+= 1
			return term.bold(term.green("PASSED ")) + protocol_path[len(config.protocols):] + "\n" + message
