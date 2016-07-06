class Settings:
	def __init__(self, args):
		self.protocols = args.protocols
		self.benchmark = args.benchmark.name
		self.tamarin = args.tamarin.name
		self.contingency = args.contingency
		self.repitions = args.repitions
		self.absolute = args.max
		if args.flags is not None:
			self.userFlags = args.flags
		else:
			self.userFlags = ""