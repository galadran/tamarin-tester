import config
import os

def getGitHubInfo():
	#Using Github, get the Tamarin-prover branches and latest commits
	return ""

def getLatestCommit(branch):
	#For a given Branch, return the latest commmit on Github
	return ""

def getGitHubBranches():
	#Return the possible branches we can select from,
	return ""

def getOrIngestPath(path):
	#From a path either add to database or get the ID from the database
	return 0 

def getGitCommit(dir):
	#Input: Path to Git Directory Output: Latest Commit Hash? Current Status?
	#TODO - What do we do if the Git Directory is dirty? s
	return ""

def buildTamarin(dir):
	#Input: A "standard Tamarin directory"
	#Output: A path to the built Tamarin binary
	return ""

def ingestTamarin(path):
	#Input: Path to a Tamarin Binary
	#Grabs all the relevant info and sticks it in the database
	#No Need to return anything
	return ""

def getOrBuildTamarin(dir):
	commit = getGitCommit(dir)
	if tamarinCommitExists(commit):
		return getTamarinIdByCommit(commit)
	else:
		return ingestTamarin(buildTamarin(dir))

def tamarinHashExists(hash):
	#Input File Hash, Output: True/False
	return False

def getTamarinIdByHash(hash):
	#Input File Hash, Output: ID
	return 0

def tamarinCommitExists(commit):
	#Input Commit Hash, Output: True/False
	return False

def getTamarinIdByCommit(commit):
	#Input Commit Hash, Output: ID
	#Might Require Building, getting the source or whatever. 
	return 0

def getKnownCommits(branch):
	#Look in DB and in Github and get the list of commits for a branch
	if branch == "all": 
		#TODO
		return ""
	else:
		return ""
		#Filter by Branch
	return []

def getGitBranches():
	#TODO??/
	return ""

def cmdLineToId(text):
	#Can be a path, a git directory or a git branch
	#TODO Add Option to pass by commit
	if text in getGitBranches():
		#Get Latest tamarin-binary-id from that branch
		#TODO
		if tamarinCommitExists(getLatestCommit(text)):
			return getTamarinIdByCommit(text)
		else:
			#Error or Warning we are falling back to latest Master
			config.warning("Cannot check Github, using latest known master")
			#TODO - Find fall back Tamarin, if it no longer exists
			config.fatalError("Cannot find valid Tamarin on branch " + text)			
	elif text in getKnownCommits():
		return getTamarinIdByCommit(text)
	elif os.path.isfile(text):
		return getOrIngestPath(text)
	elif os.path.isdir(text):
		return getOrBuildTamarin(text)
	else:
		#Throw ERROR
		#Unrecognised Protocol Option
		config.fatalError("Unknown Protocol Option")