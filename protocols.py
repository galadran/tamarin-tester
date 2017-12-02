import os
import db
import glob
from config import fatalError,warning,debug

def ProtoExistsByHash(hash):
	d= db.getHandle()
	d.execute('''SELECT COUNT(*) FROM protocols WHERE filehash=?''', (hash,))
	r = d.fetchone()["COUNT(*)"]
	if r == 1:
		return True
	elif r == 0:
		return False

def getProtoByHash(hash):
	d =db.getHandle()
	d.execute(''' SELECT * FROM protocols WHERE filehash=?''',(hash,))
	return d.fetchone()

def pathToId(path):
	db.updateOrIngestFile(path)
	if ProtoExistsByHash(db.getFileHash(path)):
		debug("Loading protocol at " + str(path) + "from database")
		return getProtoIdByHash(db.getFileHash(path))
	else:
		#TODO Possible infinite loop here... but only if something has gone horribly wrong
		return ingestProtocol(path)

def getProtoName(path):
	with open(path,'r') as f:
		for r in f.readlines():
			prefix = "theory " 
			if prefix == r[0:len(prefix)]:
				return r.replace(prefix,"")
		return None


def ingestProtocol(path):
	debug("Ingesting new protocol at " + str(path))
	h = db.getFileHash(path)
	t = getProtoName(path)
	if t == None:
		warning("No theory name found for new protocol at " + str(path))
		t = "UNKNOWN"
	d = 0
	db.getHandle().execute('''INSERT INTO protocols(fileHash,theoryName,isDiff) VALUES(?,?,?)''',
								(h,t,d))
	return pathToId(path) 

def presetProtocolsIds(preset):
	#Get the list of IDs matching this preset. 
	d = db.getHandle()
	if preset == "all":
		d.execute('''SELECT * FROM protocols''')
		return d.fetchall()
	elif preset == "fast":
		warning("Not yet implemented!")
		return []
	elif preset == "slow":
		warning("Not yet implemented!")
		return []
	fatalError("Invalid Option passed!")

def getProtoIdByHash(hash):
	return getProtoByHash(hash)["id"]

def cmdLineToIds(text):
	#Given the command line input, a list of protocol IDs we are interested in. 
	#Command Line input can be a file, a folder or a number of presets
	if text in ["fast","slow","all"]: #TODO Change this to either a specified max time, or diff-only vs no-diff. Optional improvment.
		return presetProtocolsIds(text)
	elif os.path.isfile(text):
		return [pathToId(text)]
	elif os.path.isdir(text):
		paths = glob.glob(text+"/**/*.spthy",recursive=True)
		results = []
		for path in paths: #Could do with this with lambda
			results.append(pathToId(path))
		return results
	else:
		fatalError("Unrecognised Protocol Option! " + str(text))
