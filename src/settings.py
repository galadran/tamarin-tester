import os

class Settings:
	def __init__(self, args):
		self.protocols = args.protocols  #Path to Protocl Directory
		self.tamarin = args.tamarin.name #Path to Tamarin Executable
		self.contingency = args.contingency #Max multiples of benchmark time to wait for
		self.repetitions = args.repetitions #How many samples to take for benchmark average
		self.absolute = args.max #Absolute max amount of time to spend per protocol
		if args.output is not None:
			self.output = args.output #Where to put the benchmark file
		else:
			self.output = default=os.getcwd()+"/benchmark.txt"
		if args.benchmark is not None:
			self.benchmark = args.benchmark #Where to read the benchmark file from
		else:
			self.benchmark = ""

		if args.flags is not None:
			self.userFlags = args.flags #Any user defined flags to pass to Tamarin
		else:
			self.userFlags = ""
