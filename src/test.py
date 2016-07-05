from shared import * 
from bench import *

def performTest(tamarin_command,protocol_path,bench_path,contingency):
	benchmarks = loadBench(bench_path)
	protocols = getValidProtocols(tamarin_command,protocol_path)
	hashes = set()
	lookup = dict()
	for p in protocols:
		h = hashlib.sha256(open(p,'rb').read()).hexdigest()
		lookup[h] = p
	hashes = set(lookup.keys())
	for b in benchmarks:
		if b[0] not in hashes:
			continue
		hashes.remove(b[0])
		print(testProtocol(tamarin_command,lookup[b[0]],contingency,b[1],b[2],b[3]))
	if len(hashes) > 0:
		print("Warning: " + len(hashes) + " have no matching benchmark")
		for h in hashes:
			print(lookup[h])	

def testProtocol(tamarin_command,protocol_path,contingency,diff,benchResults,estTime):
        #Tests a protocol
	message = ""
	flags = "--prove "
	if diff:
		flags = flags + " --diff "
	start = time.time()
	#TODO: Timeout!
	try:
		with open(os.devnull, 'w') as devnull:
			output = subprocess.check_output(tamarin_command+" "+flags+" "+ protocol_path,shell=True,stderr=devnull)
	except subprocess.CalledProcessError:
		print("Error Testing " + protocol_path)
		exit(1)
	end = time.time() - start
	end_state = parseResults(str(output).replace("\\n","\n"))
	for i in range(0,len(end_state)):
		if end_state[i][0] != benchResults[i][0]:
			print(end_state[i][0] + " " + str(benchResults[i][0]))
			print("Lemma order mismatch! Error!")
			exit(1)
		if end_state[i][1] != benchResults[i][1]:
			message += "FAILURE: "+ end_state[i][0] + " tested as " + end_state[i][1] + " but should be " + benchResults[i][1] + "\n"
		if end_state[i][2] != benchResults[i][2]:
			message += "WARNING: " + end_state[i][0] + " step count is " + row[i][2] + " but benchmarked at " + benchResults[i][2] + "\n"
	if "FAILURE" in message:
		return protocol_path + " FAILED \n" + message
	elif "WARNING" in message:
		return protocol_path + " has stepsize mismatch \n" + message
	else:
		return protocol_path + " has passed."

		
