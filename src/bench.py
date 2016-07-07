from shared import *
import time
from results import *
from blessings import Terminal
from tqdm import tqdm


term = Terminal()

class Bencher:
	def __init__(self, config):
		self.config = config
		this.failed = 0

	def benchProtocol(self,protocol_path):
		#Derive a benchmark for a particular protocol
		config = self.config
		output = ""
		diff =runAsDiff(config.tamarin,protocol_path)
		totalTime = 0.0
		for i in range(0, config.repetitions):
			start = time.time()
			try:
				with open(os.devnull, 'w') as devnull:
					#Run a benchmark for up to the maximum amount of time
					output = trimOutput(str(runWithTimeout(config.tamarin+" "+getFlags(config.userFlags,diff)+" "+ protocol_path,devnull,config.absolute)).replace("\\n","\n"))
					if "TIMEOUT" in str(output):
						tqdm.write(term.yellow(term.bold("TIMEOUT ")) + p[len(path):] + " \n")
						this.failed +=1
						break
					elif len(output) == 0:
						tqdm.write(term.yellow(term.bold("NOLEMMAS ")) + p[len(path):] + " \n")
						this.failed +=1
						break #No need to repeat if there is nothing to test
			except CalledProcessError:
				print(term.red("ERROR") + " benchmarking " + protocol_path[len(paths):])
				exit(1)
			end = time.time() - start
			totalTime += end
		return outputToResults(output,protocol_path,diff,totalTime/config.repetitions)

	def performBenchmark(self):
		#Perform a benchmark on all passed protocols
		config = self.config
		protocols = getValidProtocols(config.tamarin,config.protocols)
		if len(protocols) == 0:
			print(term.red("ERROR") + " No valid protocols!")
			exit(1)
		output = open(config.output,'w')
		for p in tqdm(protocols,leave=True,desc="Benchmarking protocols"):
			output.write(resultToString(self.benchProtocol(p))+"\n")
		self.original = len(getProtocols(config.protocols)
		self.failed += self.original - len(protocols)
		self.printSummary()
		print("Benchmark written to " + config.output)
		
	def printSummary(self):
		#'Pretty Print' a summary based on our counters
		print("=====================================")
		print("============== " + term.bold("Summary") + " ==============")
		print("=====================================")
		print(term.bold("TOTAL: " + str(self.original)))
		if self.failed != 0:
			print(term.bold(term.red("FAILED: " + str(self.failed))))
		else:
			print(term.bold(term.green("FAILED: " + str(self.failed))))
		if self.failed == 0:
			print(term.bold(term.green("PASSED: " + str(self.original - self.failed ))))
		elif self.original - self.failed > 0:
			print(term.bold(term.yellow("PASSED: " + str(self.original - self.failed ))))
		else:
			print(term.bold(term.red("PASSED: " + str(self.original - self.failed ))))

