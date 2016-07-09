import ast
import hashlib
import sys
import traceback
from blessings import Terminal

term = Terminal()

class Result:
	def __init__(self,fileHash,diff,lemmas,avgTime):
		self.fileHash = str(fileHash)
		self.diff = int(diff)
		self.lemmas = lemmas #need to assert this is a list of 3-tuples
		self.avgTime = float(avgTime)

def compareResults(testOutput,bench):
	#This function compares two Results objects returns a message describing any discrepancies
	message = ""
	#For  each lemma
	for i in range(0,len(testOutput)):
		if testOutput[i][0] != bench.lemmas[i][0]:
			#This should literally never happen, but a sanity check never hurt the sane
			print(testOutput[i][0] + " " + str(bench.lemmas[i][0]))
			print(term.red("ERROR")+ " Lemma order mismatch")
			exit(1)
		testSteps = int(testOutput[i][2])
		benchSteps  = int(bench.lemmas[i][2])
		#Check for a mistmatch on result (verified/falsfied)
		if testOutput[i][1] != bench.lemmas[i][1]:
			message += term.bold(term.red("\t INCORRECT: "))+ testOutput[i][0] + " was: " + bench.lemmas[i][1] + " now: " + testOutput[i][1] + "\n"
		#Check for a change in step count
		if testSteps > benchSteps:
			message += term.bold(term.yellow("\t STEPSIZE INC: ")) + testOutput[i][0] +" was: " + str(benchSteps) + " now: " + str(testSteps) + "\n"
		if testSteps < benchSteps:
			message += term.bold(term.yellow("\t STEPSIZE DEC: ")) + testOutput[i][0] +" was: " + str(benchSteps) + " now: " + str(testSteps) + "\n"
	return message

def outputToResults(output, path, diff,avgTime):
	#Create a results object out of TRIMMED Tamarin Output
	fileHash = hashlib.sha256(open(path, 'rb').read()).hexdigest()
	if "TIMEOUT" in output:
		return Result(fileHash,diff,"TIMEOUT",0.0)
	elif len(output) == 0:
		return Result(fileHash,diff,"NOLEMMAS",0.0)
	return Result(fileHash,diff,extractLemmas(output),avgTime)

def trimOutput(output):
	#Records all important lines between Summary of Summary and end of output
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
	#Parses lemma lines into Records.
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
	#Return a new Results object from a stored string
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
	benchmarks = list()
	flags = ""
	for line in f:
		if line[1] == "#":
			continue
		else:
			benchmarks.append(stringToResults(line))
	return (flags,benchmarks)
