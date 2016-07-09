from blessings import Terminal

VERSION = "Tamarin Tester v0.9"
DESCRIPTION = "This program can be used to generate benchmark files for Tamarin which record correct results for a directory of protocols. Then it can be used to test an altered Tamarin compilation for correctness by comparing against these results. First navigate to a directory containing finished protocols and run Tamarin-Tester GOOD_TAMARIN_PATH. Then run Tamarin-Tester DEV_TAMARIN_PATH --b benchmark.txt and inspect the results."

TERMINAL = Terminal()

ERROR = TERMINAL.bold(TERMINAL.red("ERROR "))
INFORMATIONAL = TERMINAL.bold(TERMINAL.blue("INFORMATIONAL "))
WARNING = TERMINAL.yellow(TERMINAL.bold("WARNING "))

CHECK_TIMEOUT= TERMINAL.red(TERMINAL.bold("CHECK TIMEOUT "))
MALFORMED= TERMINAL.bold(TERMINAL.red("\t MALFORMED"))
BENCH_TIMEOUT= TERMINAL.red(TERMINAL.bold("BENCH TIMEOUT "))
NO_LEMMAS= TERMINAL.yellow(TERMINAL.bold("NO LEMMAS "))

INCORRECT= TERMINAL.bold(TERMINAL.red("\t INCORRECT: "))
STEPSIZE_INC= TERMINAL.bold(TERMINAL.yellow("\t STEPSIZE INC: "))
STEPSIZE_DEC= TERMINAL.bold(TERMINAL.yellow("\t STEPSIZE DEC: "))
TIMEOUT= TERMINAL.bold(TERMINAL.red("\t TIMEOUT "))

OVERTIME= TERMINAL.yellow(TERMINAL.bold("OVERTIME "))
MISSING= TERMINAL.yellow(TERMINAL.bold("MISSING "))
FAILED= TERMINAL.bold(TERMINAL.red("FAILED "))
PASSED= TERMINAL.bold(TERMINAL.green("PASSED "))

