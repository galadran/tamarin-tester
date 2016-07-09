from tqdm import tqdm
from time import time

from shared import *
from results import resultToString
from interface import Tamarin

class Bencher:
	def __init__(self, config):
		self.config = config
		self.failed = 0
		self.check = 0
		self.nolemmas = 0
		self.tamarin = Tamarin(config)
		
	def estBenchTime(self):
		#Print a worst case time estimate
		count = len(getUniqueProtocols(self.config.protocols))
		runtime = count * (self.config.checkTime + self.config.absolute * self.config.repetitions)
		print(INFORMATIONAL + "WORST CASE time to complete benchmark is " + prettyTime(runtime))

	def getValidProtocols(self):
		#Given a list of protocols, check well-formedness of each
		validProtocols= list()
		start = time()
		for p in tqdm(getUniqueProtocols(self.config.protocols),leave=False,smoothing=0.0,desc="Well Formedness Checks"):
			vp = validNormProtocol(self.tamarin,p,self.config.checkTime)
			vdp = validDiffProtocol(self.tamarin,p,self.config.checkTime)
			if vp !=1 and vdp != 1:
				if vp + vdp < 0:
					tqdm.write(CHECK_TIMEOUT + p[len(path):])
				else:
					tqdm.write(MALFORMED + p[len(path):])
				continue
			else:
				validProtocols.append(p)
		td = time() - start
		print(INFORMATIONAL + "Finished well-formedness checks in " + prettyTime(td))
		return validProtocols
		
	def benchProtocol(self,protocol_path):
		#Derive a benchmark for a particular protocol
		config = self.config
		output = ""
		diff = runAsDiff(self.tamarin,protocol_path,self.config.checkTime)
		totalTime = 0.0
		for i in range(0, config.repetitions):
			start = time()
			output = self.tamarin.getResults(protocol_path,diff,config.absolute)
			if "TIMEOUT" in output.lemmas:
				tqdm.write(BENCH_TIMEOUT + protocol_path[len(config.protocols):])
				self.failed +=1
				break
			elif "NOLEMMAS" in output.lemmas:
				tqdm.write(NO_LEMMAS + protocol_path[len(config.protocols):])
				self.nolemmas +=1
				break #No need to repeat if there is nothing to test
			end = time() - start
			totalTime += end
		output.avgTime = totalTime/config.repetitions
		return output

	def performBenchmark(self):
		#Perform a benchmark on all passed protocols
		config = self.config
		print(INFORMATIONAL+"Validating protocols...")
		files = getUniqueProtocols(self.config.protocols)
		self.original = len(files)
		protocols = self.getValidProtocols()
		if len(protocols) == 0:
			print(ERROR + " No valid protocols!")
			exit(1)
		output = open(config.output,'w')
		print(INFORMATIONAL + "Benchmarking protocols...")
		start = time()
		for p in tqdm(protocols,leave=False,smoothing=0.0,desc="Benchmarking protocols"):
			output.write(resultToString(self.benchProtocol(p))+"\n")
		td = time() - start
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


