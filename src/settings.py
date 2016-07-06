import os

class Settings:
	def __init__(self, args):
		self.protocols = args.protocols
		self.tamarin = args.tamarin.name
		self.contingency = args.contingency
		self.repitions = args.repitions
		self.absolute = args.max
		if args.output is not None:
			self.output = args.output
		else:
			self.output = default=os.getcwd()+"/benchmark.txt"
		if args.benchmark is not None:
			self.benchmark = args.benchmark
		else:
			self.benchmark = ""
		
		if args.flags is not None:
			self.userFlags = args.flags
		else:
			self.userFlags = ""