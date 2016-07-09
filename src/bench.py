from shared import *
import time
from results import *
from tqdm import tqdm
import time
from constants import * 

class Bencher:
	def __init__(self, config):
		self.config = config
		self.failed = 0
		self.check = 0
		self.nolemmas = 0
		self.parser = Parser(config)

	def estBenchTime(self):
		#Print a worst case time estimate
		count = len(self.parser.getProtocols())
		runtime = count * (self.config.checkTime + self.config.absolute * self.config.repetitions)
		print(INFORMATIONAL + "WORST CASE time to complete benchmark is " + prettyTime(runtime))
		
	def benchProtocol(self,protocol_path):
		#Derive a benchmark for a particular protocol
		config = self.config
		output = ""
		diff =self.parser.runAsDiff(protocol_path)
		protFlags = extractFlags(protocol_path)
		totalTime = 0.0
		for i in range(0, config.repetitions):
			start = time.time()
			try:
				with open(os.devnull, 'w') as devnull:
					#Run a benchmark for up to the maximum amount of time
					output = str(runWithTimeout(config.tamarin+" "+getFlags(config.userFlags,1, diff,protFlags)+" "+ protocol_path,devnull,config.absolute)).replace("\\n","\n")
					filtered = trimOutput(output)
					if "TIMEOUT" in output:
						tqdm.write(BENCH_TIMEOUT + protocol_path[len(config.protocols):])
						self.failed +=1
						break
					elif len(filtered) == 0:
						tqdm.write(NO_LEMMAS + protocol_path[len(config.protocols):])
						self.nolemmas +=1
						break #No need to repeat if there is nothing to test
			except CalledProcessError:
				print(ERROR + " benchmarking " + protocol_path[len(paths):])
				exit(1)
			end = time.time() - start
			totalTime += end
		return outputToResults(filtered,protocol_path,diff,totalTime/config.repetitions,protFlags)

	def performBenchmark(self):
		#Perform a benchmark on all passed protocols
		config = self.config
		print(INFORMATIONAL+"Validating protocols...")
		files = self.parser.getUniqueProtocols()
		self.original = len(files)
		protocols = self.parser.getValidProtocols(files)
		if len(protocols) == 0:
			print(ERROR + " No valid protocols!")
			exit(1)
		output = open(config.output,'w')
		print(INFORMATIONAL + "Benchmarking protocols...")
		start = time.time()
		for p in tqdm(protocols,leave=False,smoothing=0.0,desc="Benchmarking protocols"):
			output.write(resultToString(self.benchProtocol(p))+"\n")
		td = time.time() - start
		print(INFORMATIONAL + "Finished benchmarking in " + prettyTime(td) + " seconds")
		print(INFORMATIONAL + "Benchmark written to " + config.output)
		self.check = self.original - len(protocols)
		self.printSummary()

		
	def printSummary(self):
		#'Pretty Print' a summary based on our counters
		print("=====================================")
		print("============== " + TERMINAL.bold("Summary") + " ==============")
		print("=====================================")
		print(TERMINAL.bold("TOTAL: " + str(self.original)))
		if self.check > 0:
			print(TERMINAL.bold(TERMINAL.red("FAILED CHECK: " + str(self.check))))		
		if self.failed > 0:
			print(TERMINAL.bold(TERMINAL.red("FAILED BENCHMARK: " + str(self.failed))))
		if self.nolemmas > 0: 
			print(TERMINAL.bold(TERMINAL.yellow("NO LEMMAS: " + str(self.nolemmas))))
		if self.original - self.failed - self.nolemmas > 0:
			print(TERMINAL.bold(TERMINAL.green("SUCCESSFUL: " + str(self.original - self.failed - self.check -self.nolemmas ))))
		print("=====================================")
		print("=====================================")
		print("=====================================")


