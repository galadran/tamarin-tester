from shared import *
import time
from results import *
from blessings import Terminal
from tqdm import tqdm


term = Terminal()

class Bencher:
	def __init__(self, config):
		self.config = config
		self.failed = 0
		self.check = 0
		self.parser = Parser(config)

	def benchProtocol(self,protocol_path):
		#Derive a benchmark for a particular protocol
		config = self.config
		output = ""
		diff =self.parser.runAsDiff(protocol_path)
		totalTime = 0.0
		for i in range(0, config.repetitions):
			start = time.time()
			try:
				with open(os.devnull, 'w') as devnull:
					#Run a benchmark for up to the maximum amount of time
					output = trimOutput(str(runWithTimeout(config.tamarin+" "+getFlags(config.userFlags,diff)+" "+ protocol_path,devnull,config.absolute)).replace("\\n","\n"))
					if "TIMEOUT" in str(output):
						tqdm.write(term.yellow(term.bold("TIMEOUT ")) + protocol_path[len(config.protocols):] + " \n")
						self.failed +=1
						break
					elif len(output) == 0:
						tqdm.write(term.yellow(term.bold("NOLEMMAS ")) + protocol_path[len(config.protocols):])
						self.failed +=1
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
		protocols = self.parser.getValidProtocols()
		if len(protocols) == 0:
			print(term.red("ERROR") + " No valid protocols!")
			exit(1)
		output = open(config.output,'w')
		if len(config.userFlags) != 0:
			output.write("$"+config.userFlags)
		print("Benchmarking protocols, any failures will be listed below")
		for p in tqdm(protocols,leave=True,desc="Benchmarking protocols"):
			output.write(resultToString(self.benchProtocol(p))+"\n")
		self.original = len(getProtocols(config.protocols))
		self.check = self.original - len(protocols)
		self.printSummary()
		print("Benchmark written to " + config.output)
		
	def printSummary(self):
		#'Pretty Print' a summary based on our counters
		print("=====================================")
		print("============== " + term.bold("Summary") + " ==============")
		print("=====================================")
		print(term.bold("TOTAL: " + str(self.original)))
		if self.check > 0:
			print(term.bold(term.red("FAILED CHECK: " + str(self.check))))		
		if self.failed > 0:
			print(term.bold(term.red("FAILED BENCHMARK: " + str(self.failed))))
		if self.original - self.failed > 0:
			print(term.bold(term.green("SUCCESSFUL: " + str(self.original - self.failed ))))
		print("=====================================")
		print("=====================================")
		print("=====================================")


