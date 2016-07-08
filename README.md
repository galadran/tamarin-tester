#Tamarin-Tester

##Introduction
This project is a lightwight black box tester for the [Tamarin Prover](https://github.com/tamarin-prover/tamarin-prover)

It aims to support rapid development of the Tamarin Prover by allowing developers to regression test their builds with in a timely and clear manner. It allows for the benchmarking of a suite of protocols against a known-good build of Tamarin and then for development builds to be tested against this benchmark. 

The tool automatically tests the quickest to verify protocols first in order to establish as quickly as possible whether a build is suffering issues. Additionally users can pass in maximum limits on how long to wait before assuming Tamarin will not terminate. 

##In Action
###Benchmarking
<a href="https://asciinema.org/a/azopzkvcgctzc5s7tyo76ryvz?speed=30"><img src="https://asciinema.org/a/azopzkvcgctzc5s7tyo76ryvz.png" alt="Classic" width="400" border="0"></a>
###A failing test
<a href="https://asciinema.org/a/3sr38jrk8hijjupq9fbqgxwuc?speed=7"><img src="https://asciinema.org/a/3sr38jrk8hijjupq9fbqgxwuc.png" alt="Classic" width="400" border="0"></a>
###A passing test
<a href="https://asciinema.org/a/58t0e3v6cltr7jqajqijwzq8r?speed=7"><img src="https://asciinema.org/a/58t0e3v6cltr7jqajqijwzq8r.png" alt="Classic" width="400" border="0"></a>

###Quickstart
####Installation
The easiest method is to install Python3 and PyInstaller, git clone the directory and inside run 

```
pyinstaller src/tamarin-tester.py --onefile
```

which will produce a binary for your system inside dist/ 

An already built binary for 64-bit Ubuntu 16.04 is on the Releases page, but has only been tested on one machine. 

####Building a benchmark
Firstly, we need to produce a benchmark file from a known-good build of tamarin
```
tamarin-tester TAMARIN -p PROTOCOLS
```
Where `TAMARIN` is the path to the known-good tamarin build you want to benchmark, on a standard install this is `~/.local/bin/tamarin-prover` and `PROTOCOLS` is the path to the directory of protocols you want to benchmark. Note this parameter is optional and will default to the current working directory if omitted. 

This will run the benchmark and disply a live progress report. The benchmark file will be output as `benchmark.res` in the current working directory. This benchmark file stores the hash of each inspected file and for each contained lemma, stores whether Tamarin proved or falisfied it and how many steps it took. Furthermore the proof time in seconds is stored.

####Testing a new build
```
tamarin-tester TAMARIN -p PROTOCOLS -b BENCHMARK
```
Where `TAMARIN` is the path to the development tamarin build you want to test, `PROTOCOLS` is the path to the directory of protocols you want to test the tamarin build against and `BENCHMARK` is a path to the `benchmark.res` file you wish to test against. 

This will run the test and display a live progress report. Pay attention to the estimated time as testing can take some time. It will finish with a summary detailing one of `PASS`, `FAIL`, `????`. The first two are self-explanatory. `????` is reported when their are protocol files in the directory which have no benchmark, when their are protocol files in the directory which have no lemmas (usually because of an `IFDEF`) or if the step counts change for a particular proof, but otherwise no actual failures occur.  

##Global Command Line Options
Also see the mode specific options below

| Command | Default | Description | 
| --- | --- | --- |
| `TAMARIN` |None| The only mandatory argument, the path to the known-good tamarin build you want to benchmark|
| `-p`, `--protocols` |$PWD| The directory to recursively scan for `.spthy` files|
| `-mp`, `--maxproof` |30| (integer) max time in seconds to run a proof for|
| `-mc`, `--maxcheck` |10| (integer) max time in seconds to test for wellformedness|
| `-v`, `--verbose` |FLAG| Enables verbose logging|

##Generating a benchmark
This is the default mode
###Command Line Options
Also see the global options above! 

| Command | Default | Description | 
| --- | --- | --- |
| `-r`, `--repetitions`|3| Number of samples to take for average proof running time|
| `-o`, `--output` |PWD/benchmark.res| Where to output the resulting benchmark file|
| `-f`, `--flags` |NA| Flags to passed to Tamarin|

###Tag Meanings

| Tag | Meaning |
| --- | --- |
| CHECK TIMEOUT | Checking well-formedness for the given protocol timed out (`maxcheck`) and it will be omitted from the benchmark |
| MALFORMED | The given protcol is not well-formed and it will be omitted from the benchmark |
| BENCH TIMEOUT | Tamarin did not terminate in the time specified (`maxproof`) and this protocol will be omitted from the benchmark|
| NO LEMMAS | This protocol did not contain any lemmas to prove, so there is nothing to benchmark, a flag may need to be passed to Tamarin to enable an `IFDEF` |
| INFORMATIONAL | A message for the user from tamarin-tester itself |
| ERROR | A fatal error occurred and the program will terminate |

##Testing a build
This mode is selected when the `-b` or `--benchmark` flag is passed. Flag for Tamarin are parsed from the benchmark file
###Command Line Options
Also see the global options above! 

| Command | Default | Description | 
| --- | --- | --- |
| `-b`, `--benchmark` |NA| The benchmark file to load to test against|
| `-c`, `--contingency` |2| (integer) factor to multiply expected running time by|

###Protocol Tag Meanings

| Tag | Meaning |
| --- | --- |
| PASSED | This protocol has identical lemma results and stepsizes under the new tamarin build as did under the benchmarked Tamarin build |
| WARNING | This protocol has identical lemma results (true/false) but there are minor differences e.g. stepsize |
| NO LEMMAS | The benchmarked protocol had no lemmas and consequently there is nothing to compare |
| MISSING | The protocol was in the protocols directory but not in the benchmark file and hence could not be checked |
| OVERTIME | The average runtime for this protocol is higher than the max allowed run time and hence it is expected to timeout |
| FAILED | The new Tamarin build disagress with the benchmarked build for one or more lemmas |

###Reason Tag Meanings

| Tag | Meaning |
| --- | --- |
| STEPSIZE INC | This lemma took more steps to prove with the new build |
| STEPSIZE DEC | This lemma took less steps to prove with the new build|
| INCORRECT | This lemma has a different truth value with the new build |
| TIMEOUT | This protocol failed to terminate in the allotted time which is the contingency value (argument) c * avgRunTime (from the benchmark file) for the protocol file |

###Other tags

| Tag | Meaning |
| --- | --- |
| INFORMATIONAL | A message for the user from tamarin-tester itself |
| ERROR | A fatal error occurred and the program will terminate |

##Benchmark Files
This have a relatively simple structure. Comment lines begin with `#`, there should be a single FLAG line which begins with `$` and then each protocol occupies a single line with the format 

```
SHA-256 Hash | Diff | List of (Lemma Name, Validity, Steps) tuples | Average Runtime
```

##Internals 
TODO
