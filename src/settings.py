import os

class Settings:
	def __init__(self, args):
		self.protocols = args.protocols  #Path to Protocl Directory
		self.tamarin = args.tamarin.name #Path to Tamarin Executable
		self.contingency = args.contingency #Max multiples of benchmark time to wait for
		self.repetitions = args.repetitions #How many samples to take for benchmark average
		self.verbose = args.verbose
		self.removeOvertime = args.overtime
		self.absolute = 0.0
		self.checkTime = 0.0
		if args.output is not None:
			self.output = args.output #Where to put the benchmark file
		else:
			self.output = default=os.getcwd()+"/benchmark.res"
		if args.benchmark is not None:
			self.benchmark = args.benchmark #Where to read the benchmark file from
			if args.maxproof is not None:
				self.absolute = args.maxproof
			if args.maxcheck is not None:
				self.checkTime = args.maxcheck
		else:
			self.benchmark = ""
			self.absolute = args.maxproof
			self.checkTime = args.maxcheck

		if args.flags is not None:
			self.userFlags = args.flags #Any user defined flags to pass to Tamarin
		else:
			self.userFlags = ""
		