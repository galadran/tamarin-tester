from config import warning, fatal_error
import protocols
import tamarin
#verbose,debug

def getOrGenerateResults(tamarinId, protocolId):
	#TODO
	return ""

def run_evaluation(args):
	#Args Contains: test_binary,test_protocols,reference,failfast,max,performance
	ids = protocols.cmdLineToIds(args.test_protocols)
	if len(ids) == 0:
		#THROW ERROR
		fatal_error("No protocols found in selection!")
	#TODO Print Missing / Warn
	testTamarinId = tamarin.cmdLineToId(args.test_binary)
	refTamarinId = tamarin.cmdLineToId(args.reference)
	if not tamarin.checkExists(testTamarinId) or not tamarin.checkExists(refTamarinId):
		#Print Warning / Error
		fatal_error("At least one Tamarin binary cannot be found")
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