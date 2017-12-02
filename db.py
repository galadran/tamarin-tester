import sqlite3
from hashlib import sha256
from datetime import datetime
import os 

connection = []
d = []

fileTable = '''CREATE TABLE IF NOT EXISTS files(
				id INTEGER PRIMARY KEY, 
				fileHash TEXT, 
				filePath TEXT UNIQUE,
				firstSeen TIMESTAMP,
				lastSeen TIMESTAMP
				)'''

protocolTable = '''CREATE TABLE IF NOT EXISTS protocols(
				id INTEGER PRIMARY KEY,
				fileHash TEXT UNIQUE,
				theoryName TEXT,
				isDiff INTEGER
				)'''


def openDatabase(path):
	global d, connection
	connection = sqlite3.connect(path)
	connection.row_factory = sqlite3.Row
	d = connection.cursor()
	createDatabase()

def createDatabase():
	#Build the tables in the Database
	d.execute(fileTable)
	d.execute(protocolTable)
	#TODO The Other tables
	saveDatabase();
	return ""

def saveDatabase():
	connection.commit()

def getHandle():
	return d

def getFileHash(path):
	return sha256(open(path,'rb').read()).hexdigest()

def updateOrIngestFile(path):
	if knownFile(path):
		updateFile(path)
	else:
		ingestFile(path)

def knownFile(path):
	d.execute('''SELECT COUNT(*) FROM files WHERE filePath=?''', (path,))
	r = d.fetchone()["COUNT(*)"]
	if r == 1:
		return True
	elif r == 0:
		return False

def getWorkingFile(hash):
	d.execute('''SELECT * FROM files WHERE fileHash=?''', (hash,))
	for r in d.fetchall():
		if updateFile(r["filePath"]):
			return r["filePath"]
	return None

def updateFileSeen(path):
	d.execute('''UPDATE files SET lastSeen = ?
			WHERE filePath=?''', (datetime.now(),path))

def deleteFile(path):
	d.execute('''DELETE FROM files WHERE filePath=?'''(path,))

def updateFile(path):
	if not os.path.isfile(path):
		deleteFile(path)
		return False
	h = getFileHash(path)
	d.execute('''SELECT * FROM files WHERE filePath=?''', (path,))
	if h != d.fetchone()["fileHash"]:
		deleteFile(path)
		return False
	else:
		updateFileSeen(path)
		return True

def ingestFile(path):
	d.execute('''INSERT INTO files(fileHash,filePath,firstSeen,lastSeen) VALUES(?,?,?,?)''',
								(getFileHash(path),path,datetime.now(),datetime.now()))