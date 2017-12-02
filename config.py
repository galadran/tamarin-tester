from sys import exit

#Handles global configuration
#Modules are the basis for the singleton pattern in Python
#Changes made to variables at the module level are reflected in all modules importing it. 
#These values are set by main when it parses its arguments.
VERBOSE = False
DEBUG = False
SIMPLE = False
DATABASE_PATH = ""

def debug(text):
	if DEBUG:
		print(text)

def fatalError(text):
	print("FATAL ERROR: " + str(text))
	exit(-1000)

def warning(text):
	print("WARNING: " + str(text))
