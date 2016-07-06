import ast
import hashlib
import sys 
import traceback
from blessings import Terminal

term = Terminal()

class Result:
	def __init__(self,fileHash,diff,lemmas,avgTime):
		#Do things
		self.fileHash = str(fileHash)
		self.diff = int(diff)
		self.lemmas = lemmas #need to assert this is a list of 3-tuples
		self.avgTime = float(avgTime)
	
def outputToResults(output, path, diff,avgTime):
	#Return a new Results object
	#Given the output from Tamarin, parse the summary
	#Output should be a list of tuples (lemma_name,result,steps)
	fileHash = hashlib.sha256(open(path, 'rb').read()).hexdigest()
	if "TIMEOUT" in output:
		return Result(fileHash,diff,"TIMEOUT",0.0)
	elif len(output) == 0:
		return Result(fileHash,diff,"NOLEMMAS",0.0)
	return Result(fileHash,diff,extractLemmas(output),avgTime)

def trimOutput(output):
	reached = False
	filtered = ""
	for line in output.split('\n'):
		if reached and not line =="" and not"=" in line and not "'" in line and not '"' in line:
			if not len(filtered) == 0:
				filtered += "\n"
			filtered += line
		if "analyzed: " in line:
			reached = True
	return filtered
			
def extractLemmas(filtered):
	try:
		lemmas = list()
		if "DiffLemma" in filtered:
			for line in filtered.split("\n"):
				state = "UNKNOWN"
				(side,name,b) = tuple(line.split(":"))
				(c,d) = tuple(b.split("("))
				if "falsified" in c:
					state = "FALSE"
				else:
					state = "TRUE"
				steps = ''.join(x for x in d if x.isdigit())
				lemmas.append((side+name,state,steps))
		else:
			for line in filtered.split("\n"):
				state = "UNKNOWN"
				(name,b) = tuple(line.split(":"))
				(c,d) = tuple(b.split("("))
				if "falsified" in c:
					state = "FALSE"
				else:
					state = "TRUE"
				steps = ''.join(x for x in d if x.isdigit())
				lemmas.append((name,state,steps))
		return lemmas
	except:
		print(term.red("ERROR") + " failed to parse Tamarin output")
		print(filtered)
		exit(1)
		return "NONE"

def stringToResults(val):
	#Return a new Results object
	row = val.split("|")
	if row[2] == "TIMEOUT" or row[2] == "NOLEMMAS":
		return Result(row[0],row[1],row[2],row[3])
	return Result(row[0],row[1],ast.literal_eval(row[2]),row[3])
		
def resultToString(res):
	#Return a string representing a result object
	if "TIMEOUT" in str(res.lemmas):
		return ""
	return res.fileHash + "|" + str(res.diff) + "|" +str(res.lemmas) + "|" + str(res.avgTime)
		
def fileToResults(f):
	#Return a list of results objects.
	#Returns a list of benchmark results
	benchmarks = list()
	for line in f:
		benchmarks.append(stringToResults(line))
	return benchmarks