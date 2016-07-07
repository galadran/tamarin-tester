from shared import *
import time
from results import *
from blessings import Terminal
from tqdm import tqdm
import time

term = Terminal()

class Bencher:
	def __init__(self, config):
		self.config = config
		self.failed = 0
		self.check = 0
		self.nolemmas = 0
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
					output = str(runWithTimeout(config.tamarin+" "+getFlags(config.userFlags, diff)+" "+ protocol_path,devnull,config.absolute)).replace("\\n","\n")
					filtered = trimOutput(output)
					if "TIMEOUT" in output:
						tqdm.write(term.red(term.bold("BENCH TIMEOUT ")) + protocol_path[len(config.protocols):])
						self.failed +=1
						break
					elif len(filtered) == 0:
						tqdm.write(term.yellow(term.bold("NO LEMMAS ")) + protocol_path[len(config.protocols):])
						self.nolemmas +=1
						break #No need to repeat if there is nothing to test
			except CalledProcessError:
				print(term.red("ERROR") + " benchmarking " + protocol_path[len(paths):])
				exit(1)
			end = time.time() - start
			totalTime += end
		return outputToResults(filtered,protocol_path,diff,totalTime/config.repetitions)

	def performBenchmark(self):
		#Perform a benchmark on all passed protocols
		config = self.config
		print("Validating protocols...")
		protocols = self.parser.getValidProtocols()
		if len(protocols) == 0:
			print(term.red("ERROR") + " No valid protocols!")
			exit(1)
		output = open(config.output,'w')
		if len(config.userFlags) != 0:
			output.write("$"+config.userFlags)
		print("Benchmarking protocols...")
		start = time.time()
		for p in tqdm(protocols,leave=False,desc="Benchmarking protocols"):
			output.write(resultToString(self.benchProtocol(p))+"\n")
		td = time.time() - start
		print("Finished benchmarking in " + prettyTime(td) + " seconds")
		self.original = len(self.parser.getProtocols())
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
		if self.nolemmas > 0: 
			print(term.bold(term.yellow("NO LEMMAS: " + str(self.nolemmas))))
		if self.original - self.failed - self.nolemmas > 0:
			print(term.bold(term.green("SUCCESSFUL: " + str(self.original - self.failed - self.check -self.nolemmas ))))
		print("=====================================")
		print("=====================================")
		print("=====================================")


