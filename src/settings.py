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
		self.input = ""
		self.output = ""
		if args.flags is not None:
			self.userFlags = args.flags #Any user defined flags to pass to Tamarin
		else:
			self.userFlags = ""
		