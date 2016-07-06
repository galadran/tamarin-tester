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
		for b in tqdm(sorted(self.benchmarks, key=lambda bench: bench.avgTime),leave=False):
			if b.fileHash not in hashes or self.ignoreBench(b):
				continue
			hashes.remove(b.fileHash)
			if (not b.diff and validateProtocol(config.tamarin,self.hashToPath[b.fileHash])) or (b.diff and validDiffProtocol(config.tamarin,self.hashToPath[b.fileHash])):
					tqdm.write(self.testProtocol(self.hashToPath[b.fileHash],b),end="")
			else:
				tqdm.write(term.bold(term.red("FAILED ")) + self.hashToPath[b.fileHash][len(path):] + "\n" + text.red("Failure") + " malformed but should be well-formed")
		if len(hashes) > 0:
			print(term.yellow("Warning: ") + str(len(hashes)) + " have no matching benchmark")
			for h in hashes:
				print(self.hashToPath[h])

	def compareResults(self,testOutput,bench):
		message = ""
		for i in range(0,len(testOutput)):
			if testOutput[i][0] != bench.lemmas[i][0]:
				print(testOutput[i][0] + " " + str(bench.lemmas[i][0]))
				print(term.red("ERROR")+ " Lemma order mismatch")
				exit(1)
		if testOutput[i][1] != bench.lemmas[i][1]:
			message += term.red("FAILURE: ")+ testOutput[i][0] + " tested as " + testOutput[i][1] + " but should be " + bench.lemmas[i][1] + "\n"
		if testOutput[i][2] > bench.lemmas[i][2]:
			message += term.yellow("WARNING: ") + testOutput[i][0] + " step count increased to " + testOutput[i][2] + "from benchmark at " + bench.lemmas[i][2] + "\n"
		if testOutput[i][2] < bench.lemmas[i][2]:
			message += "INFORMATIONAL: " + testOutput[i][0] + " step count decreased to " + testOutput[i][2] + "from benchmark at " + bench.lemmas[i][2] + "\n"
		return message

	def testProtocol(self,protocol_path,bench):
		config = self.config
		message = ""
		start = time.time()
		try:
			with open(os.devnull, 'w') as devnull:
				output = runWithTimeout(config.tamarin+" "+getFlags(config.userFlags,bench.diff)+" "+ protocol_path,devnull,min(config.absolute,bench.avgTime*config.contingency))
				if "TIMEOUT" in str(output):
					message = term.yellow("Warning ") + "proof timed out."
					return term.bold(term.yellow("WARNING ")) + protocol_path[len(config.protocols):] + "\n" + message
		except CalledProcessError:
			print(term.red("ERROR") + " Testing " + protocol_path[len(config.protocols):])
			exit(1)
		end = time.time() - start
		end_state = extractLemmas(trimOutput(str(output).replace("\\n","\n")))
		message = self.compareResults(end_state,bench)
		if "FAILURE" in message:
			return term.bold(term.red("FAILED ")) + protocol_path[len(config.protocols):] + "\n" + message
		elif "WARNING" in message:
			return term.bold(term.yellow("WARNING ")) + protocol_path[len(config.protocols):] + "\n" + message
		else:
			return term.bold(term.green("PASSED ")) + protocol_path[len(config.protocols):] + "\n" + message

			
