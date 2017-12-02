from config import warning, fatalError
import protocols
import tamarin
import sys
import db
#verbose,debug

def getOrGenerateResults(tamarinId, protocolId):
	#TODO
	return ""

def run_evaluation(args):
	#Args Contains: test_binary,test_protocols,reference,failfast,max,performance
	ids = protocols.cmdLineToIds(args.test_protocols)
	db.saveDatabase()
	if len(ids) == 0:
		#THROW ERROR
		fatalError("No protocols found in selection!")
	print(ids)
	sys.exit(0)
	#TODO Print Missing / Warn
	testTamarinId = tamarin.cmdLineToId(args.test_binary)
	refTamarinId = tamarin.cmdLineToId(args.reference)
	if not tamarin.checkExists(testTamarinId) or not tamarin.checkExists(refTamarinId):
		#Print Warning / Error
		fatalError("At least one Tamarin binary cannot be found")
		#Improve to be a warning and use stored results? 
		#TODO
	# Main Loop
	for p in ids:
		if not protocols.hasValidProtocolPath(p):
			#TODO Skip, Print Warning
			warning("No Valid Protocol path for " + str(p))
			continue
		resultT = getOrGenerateResults(testTamarinId,p)
		resultR = getOrGenerateResults(refTamarinId,p)
		#TODO Comparision
	#TODO Summary
	return 0 #Or another error code