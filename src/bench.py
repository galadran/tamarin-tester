from shared import *
import time
from results import * 
from blessings import Terminal
from tqdm import tqdm


term = Terminal()

class Bencher:
	def __init__(self, config):
		self.config = config
	
	def benchProtocol(self,protocol_path):
		config = self.config
		totalTime = 0.0
		output = ""
		diff =runAsDiff(config.tamarin,protocol_path)
		for i in range(0, config.repitions):
			start = time.time() 
			try:
				with open(os.devnull, 'w') as devnull:
					output = trimOutput(str(runWithTimeout(config.tamarin+" "+getFlags(config.userFlags,diff)+" "+ protocol_path,devnull,30)).replace("\\n","\n"))
					if "TIMEOUT" in str(output) or len(output) == 0: 
						break
			except CalledProcessError:
				print(term.red("ERROR") + " benchmarking " + protocol_path[len(paths):])
				exit(1)
			end = time.time() - start
			totalTime += end
		return outputToResults(output,protocol_path,diff,totalTime/config.repitions)

	def performBenchmark(self):
		config = self.config
		protocols = getValidProtocols(config.tamarin,config.protocols)
		if len(protocols) == 0:
			print(term.red("ERROR") + " No valid protocols!")
			exit(1)
		output = open(config.output,'w')
		for p in tqdm(protocols,leave=True,desc="Benchmarking protocols"):
			output.write(resultToString(self.benchProtocol(p))+"\n")
		print("Benchmark written to " + config.output)
