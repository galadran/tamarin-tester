from ast import literal_eval
from sys import exit

from shared import *

class Result:
	def __init__(self,fileHash,diff,lemmas,avgTime,flags):
		self.fileHash = str(fileHash)
		self.diff = int(diff)
		self.lemmas = lemmas #need to assert this is a list of 3-tuples
		self.avgTime = float(avgTime)
		self.flags = str(flags)

def compareResults(output,bench):
	#This function compares two Results objects returns a message describing any discrepancies
	message = ""
	#For  each lemma
	for i in range(0,len(output.lemmas)):
		if output.lemmas[i][0] != bench.lemmas[i][0]:
			#This should literally never happen, but a sanity check never hurt the sane
			print(output.lemmas[i][0] + " " + str(bench.lemmas[i][0]))
			print(ERROR+ " Lemma order mismatch")
			exit(1)
		testSteps = int(output.lemmas[i][2])
		benchSteps  = int(bench.lemmas[i][2])
		#Check for a mistmatch on result (verified/falsfied)
		if output.lemmas[i][1] != bench.lemmas[i][1]:
			message += INCORRECT + output.lemmas[i][0] + " was: " + bench.lemmas[i][1] + " now: " + output.lemmas[i][1] + "\n"
		#Check for a change in step count
		if testSteps > benchSteps:
			message += STEPSIZE_INC + output.lemmas[i][0] +" was: " + str(benchSteps) + " now: " + str(testSteps) + "\n"
		if testSteps < benchSteps:
			message += STEPSIZE_DEC + output.lemmas[i][0] +" was: " + str(benchSteps) + " now: " + str(testSteps) + "\n"
	return message
	
def stringToResults(val):
	#Return a new Results object from a stored string
	row = val.split("|")
	if row[2] == "TIMEOUT" or row[2] == "NOLEMMAS":
		return Result(row[0],row[1],row[2],row[3],row[4])
	return Result(row[0],row[1],literal_eval(row[2]),row[3],row[4])

def resultToString(res):
	#Return a string representing a result object
	return res.fileHash + "|" + str(res.diff) + "|" +str(res.lemmas) + "|" + str(res.avgTime) + "|" + str(res.flags)
	
def fileToResults(path):
	#Return a list of results objects.
	f = open(path,'r')
	benchmarks = list()
	flags = ""
	for line in f:
		if line[0] == "#":
			continue
		else:
			benchmarks.append(stringToResults(line))
	return (flags,benchmarks)
