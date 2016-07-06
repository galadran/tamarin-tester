from shared import *
from bench import *
from blessings import Terminal
from results import *
from tqdm import tqdm

term = Terminal()

class Tester:
	def __init__(self, config):
		self.config = config
		#Load protocols and benchmarks
		self.hashToPath = dict()
		for p in getProtocols(config.protocols):
			self.hashToPath[hashlib.sha256(open(p,'rb').read()).hexdigest()] = p
		self.benchmarks = fileToResults(config.benchmark)
		#Counters for results
		self.failures = 0
		self.passed = 0
		self.warning = 0
		self.missing = 0
		self.nolemmas = 0
		self.total = len(self.hashToPath.keys())

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
		for b in tqdm(sorted(self.benchmarks, key=lambda bench: bench.avgTime),leave=True,desc="Testing against benchmarks"):
			if b.fileHash not in hashes or "TIMEOUT" in b.lemmas:
				#We can ignore this benchmark as either we have no data or its not in our test input
				continue
			hashes.remove(b.fileHash)
			#NoLemmas means that the benchmark had nothing to prove and hence we cannot test here
			if "NOLEMMAS" in b.lemmas:
				self.nolemmas += 1
				tqdm.write(term.bold(term.yellow("NOLEMMAS:")) + self.hashToPath[b.fileHash][len(config.protocols):])
				continue
			#Here we check for well formedness
			if (not b.diff and validateProtocol(config.tamarin,self.hashToPath[b.fileHash])) or (b.diff and validDiffProtocol(config.tamarin,self.hashToPath[b.fileHash])):
					tqdm.write(self.testProtocol(self.hashToPath[b.fileHash],b),end="")
			else:
				#Both test and benchmark versions should agree on well formedness
				tqdm.write(term.bold(term.red("FAILED ")) + self.hashToPath[b.fileHash][len(config.protocols):] + "\n" + term.red("\t MALFORMED") + " should pass well-formedness check")
				self.failures+= 1
		#Print out protocols we could not find a benchmark for
		for h in hashes:
			self.missing+= 1
			print(term.yellow(term.bold("UNMATCHED "))+ self.hashToPath[h][len(config.protocols):])
		self.printSummary()

	def printSummary(self):
		#'Pretty Print' a summary based on our counters
		print("=====================================")
		print("============== " + term.bold("Summary") + " ==============")
		print("=====================================")
		print(term.bold("TOTAL: " + str(self.total)))
		if self.failures != 0:
			print(term.bold(term.red("FAILED: " + str(self.failures))))
		else:
			print(term.bold(term.green("FAILED: " + str(self.failures))))
		if self.warning != 0:
			print(term.bold(term.yellow("WARNED: " + str(self.warning))))
		else:
			print(term.bold(term.green("WARNED: " + str(self.warning))))
		if self.missing != 0:
			print(term.bold(term.yellow("MISSED: " + str(self.missing))))
		else:
			print(term.bold(term.green("MISSED: " + str(self.missing))))
		if self.nolemmas != 0:
			print(term.bold(term.yellow("NOLEMMAS: " + str(self.nolemmas))))
		else:
			print(term.bold(term.green("NOLEMMAS: " + str(self.nolemmas))))
		if self.passed == self.total:
			print(term.bold(term.green("PASSED: " + str(self.passed))))
		elif self.passed > 0:
			print(term.bold(term.yellow("PASSED: " + str(self.passed))))
		else:
			print(term.bold(term.red("PASSED: " + str(self.passed))))
		if self.failures > 0:
			print("=====================================")
			print("=============== " + term.red(term.bold("FAIL")) + " ================")
			print("=====================================")
		elif self.warning + self.missing > 0:
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
				output = runWithTimeout(config.tamarin+" "+getFlags(config.userFlags,bench.diff)+" "+ protocol_path,devnull,allowedTime)
				#If we TIMEOUT here, the benchmark did not and hence this is a failure
				if "TIMEOUT" in str(output):
					self.failures+= 1
					return term.bold(term.red("FAILED ")) + protocol_path[len(config.protocols):] + "\n" + term.bold(term.red("\t TIMEOUT ")) + "after " + str(allowedTime) + " seconds \n"
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
