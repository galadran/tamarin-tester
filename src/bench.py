from shared import *
import time
import ast
import hashlib

def benchProtocol(tamarin_command,protocol_path,repitions):
	#Benchmarks a protocol 
	diff = runAsDiff(tamarin_command,protocol_path)
	flags = "--prove "
	if diff:
		flags = flags + " --diff "
	totalTime = 0.0
	output = ""
	for i in range(0, repitions):
		start = time.time() 
		try:
			with open(os.devnull, 'w') as devnull:
				output = subprocess.check_output(tamarin_command+" "+flags+" "+ protocol_path,shell=True,stderr=devnull)
		except subprocess.CalledProcessError:
			print("Error benchmarking " + protocol_path)
			exit(1)
		end = time.time() - start
		totalTime += end
	end_state = parseResults(str(output).replace("\\n","\n"))
	fileHash = hashlib.sha256(open(protocol_path, 'rb').read()).hexdigest()
	return fileHash+"|"+str(diff)+ "|" + str(end_state) + "|" + str(totalTime / repitions) 

def performBenchmark(tamarin_command,protocol_path,repititions):
	start = time.time()
	protocols = getValidProtocols(tamarin_command,protocol_path)
	if len(protocols) == 0:
		print("No valid protocols!")
		exit(1)
	output = open("benchmark.txt","w")
	for p in protocols:
		output.write(benchProtocol(tamarin_command,p,repititions)+"\n")
	print("Benchmark written to 'benchmark.txt'")
	end = time.time() - start
	print("Elapsed time: " + str(end))

def loadBench(path):
        #Returns a list of benchmark results
        f = open(path,'r')
        benchmarks = list()
        for line in f:
                benchmarks.append(line.split("|"))
                benchmarks[-1][1] = int(benchmarks[-1][1])
                benchmarks[-1][2] = ast.literal_eval(benchmarks[-1][2])
                benchmarks[-1][3] = float(benchmarks[-1][3])
        return benchmarks

def parseResults(output):
        #Given the output from Tamarin, parse the summary
        #Output should be a list of tuples (lemma_name,result,steps)
        reached = False
        filtered = ""
        for line in output.split('\n'):
                if reached and not line =="" and not"=" in line and not "'" in line:
                        if not len(filtered) == 0:
                                filtered += "\n"
                        filtered += line
                if "analyzed: " in line:
                        reached = True
        results = list()
        for line in filtered.split("\n"):
                state = "UNKNOWN"
                (name,b) = tuple(line.split(":"))
                (c,d) = tuple(b.split("("))
                if "falsified" in c:
                        state = "FALSE"
                else:
                        state = "TRUE"
                steps = ''.join(x for x in d if x.isdigit())
                results.append((name,state,steps))
        return results

