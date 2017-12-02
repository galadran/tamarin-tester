import os
import db
import glob
from config import fatalError

def pathToId(path):
	if db.ProtoExistsByHash(db.getFileHash(path)):
		return db.getProtoIdByHash(db.getFileHash(path))
	else:
		return ingestProtocol(path)

def ingestProtocol(path):
	return 0 
	#Return ID, add new protocol to database

def presetProtocolsIds(preset):
	#Get the list of IDs matching this preset. 
	return []

def hasValidProtocolPath(id):
	#Check Database and get paths
	#Check hashes
	#If hashes don't match DB tehn remove path
	#Return True / False if at least one hash remains
	return False

def getProtoIdByHash(hash):
	return db.getProtoByHash(hash)["id"]

def cmdLineToIds(text):
	#Given the command line input, a list of protocol IDs we are interested in. 
	#Command Line input can be a file, a folder or a number of presets
	if text in ["fast","slow","all"]: #TODO Change this to either a specified max time, or diff-only vs no-diff. Optional improvment.
		return presetProtocolsIds(text)
	elif os.path.isfile(text):
		return [pathToId(text)]
	elif os.path.isdir(text):
		paths = glob.glob(text+"**.spthy",recursive=True)
		results = []
		for path in paths: #Could do with this with lambda
			results.append(pathToId(path))
		return results
	else:
		#TODO
		fatalError("Unrecognised Protocol Option! " + str(text))
