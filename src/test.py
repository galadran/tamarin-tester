from shared import * 
from bench import *
from blessings import Terminal
from results import * 
from tqdm import tqdm

term = Terminal()

class Tester:
	def __init__(self, config):
		self.config = config
		self.hashToPath = dict()
		for p in getProtocols(config.protocols):
			self.hashToPath[hashlib.sha256(open(p,'rb').read()).hexdigest()] = p
		self.benchmarks = fileToResults(config.benchmark)
		
		self.failures = 0
		self.passed = 0
		self.warning = 0
		self.missing = 0
		self.total = len(self.hashToPath.keys())
			
	def ignoreBench(self, b):
		if "TIMEOUT" in b.lemmas and b.avgTime > config.absolute:
			return 1
		elif "NOLEMMAS" in b.lemmas:
			return 1
		else:
			return 0

	def performTest(self):
		config = self.config
		hashes = set(self.hashToPath.keys())
		for b in tqdm(sorted(self.benchmarks, key=lambda bench: bench.avgTime),leave=True,desc="Testing against benchmarks"):
			if b.fileHash not in hashes or self.ignoreBench(b):
				continue
			hashes.remove(b.fileHash)
			if (not b.diff and validateProtocol(config.tamarin,self.hashToPath[b.fileHash])) or (b.diff and validDiffProtocol(config.tamarin,self.hashToPath[b.fileHash])):
					tqdm.write(self.testProtocol(self.hashToPath[b.fileHash],b),end="")
			else:
				tqdm.write(term.bold(term.red("FAILED ")) + self.hashToPath[b.fileHash][len(path):] + "\n" + term.red("\t MALFORMED") + " should pass well-formedness check")
				self.failures+= 1
		for h in hashes:
			self.missing+= 1
			print(term.yellow(term.bold("UNMATCHED "))+ self.hashToPath[h][len(config.protocols):])
		self.printSummary()

	def printSummary(self):
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
		if self.passed == self.total:
			print(term.bold(term.green("PASSED: " + str(self.passed))))
		elif self.passed > 0:
			print(term.bold(term.yellow("PASSED: " + str(self.passed))))
		else:
			print(term.bold(term.red("PASSED: " + str(self.passed))))

	def compareResults(self,testOutput,bench):
		message = ""
		for i in range(0,len(testOutput)):
			if testOutput[i][0] != bench.lemmas[i][0]:
				print(testOutput[i][0] + " " + str(bench.lemmas[i][0]))
				print(term.red("ERROR")+ " Lemma order mismatch")
				exit(1)
			if testOutput[i][1] != bench.lemmas[i][1]:
				message += term.bold(term.red("\t INCORRECT: "))+ testOutput[i][0] + " tested as " + testOutput[i][1] + " but should be " + bench.lemmas[i][1] + "\n"
			if testOutput[i][2] > bench.lemmas[i][2]:
				message += term.bold(term.red("\t STEPSIZE: ")) + testOutput[i][0] + " step count increased to " + testOutput[i][2] + "from benchmark at " + bench.lemmas[i][2] + "\n"
			if testOutput[i][2] < bench.lemmas[i][2]:
				message += term.bold(term.blue("\t STEPSIZE: ")) + testOutput[i][0] + " step count decreased to " + testOutput[i][2] + "from benchmark at " + bench.lemmas[i][2] + "\n"
		return message

	def testProtocol(self,protocol_path,bench):
		config = self.config
		message = ""
		start = time.time()
		allowedTime = min(config.absolute,bench.avgTime*config.contingency)
		try:
			with open(os.devnull, 'w') as devnull:
				output = runWithTimeout(config.tamarin+" "+getFlags(config.userFlags,bench.diff)+" "+ protocol_path,devnull,allowedTime)
				if "TIMEOUT" in str(output):
					self.failures+= 1
					return term.bold(term.red("FAILED ")) + protocol_path[len(config.protocols):] + "\n" + term.bold(term.red("\t TIMEOUT ")) + "after " + str(allowedTime) + " seconds \n"
		except CalledProcessError:
			print(term.red("ERROR") + " Testing " + protocol_path[len(config.protocols):])
			exit(1)
		end = time.time() - start
		end_state = extractLemmas(trimOutput(str(output).replace("\\n","\n")))
		message = self.compareResults(end_state,bench)
		if "INCORRECT" in message:
			self.failures+= 1
			return term.bold(term.red("FAILED ")) + protocol_path[len(config.protocols):] + "\n" + message
		elif "WARNING" in message:
			self.warning+= 1
			return term.bold(term.yellow("STEPSIZE")) + protocol_path[len(config.protocols):] + "\n" + message
		else:
			self.passed+= 1
			return term.bold(term.green("PASSED ")) + protocol_path[len(config.protocols):] + "\n" + message

			
