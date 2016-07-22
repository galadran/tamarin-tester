#Tamarin-Tester

##Introduction
This project is a lightwight black box tester for the [Tamarin Prover](https://github.com/tamarin-prover/tamarin-prover)

It aims to support rapid development of the Tamarin Prover by allowing developers to regression test their builds with in a timely and clear manner. It allows for the benchmarking of a suite of protocols against a known-good build of Tamarin and then for development builds to be tested against this benchmark. 

The tool automatically tests the quickest to verify protocols first in order to establish as quickly as possible whether a build is suffering issues. Additionally users can pass in maximum limits on how long to wait before assuming Tamarin will not terminate. 

##In Action
###Benchmarking
<a href="https://asciinema.org/a/9prjp6ub0lq6aio9nk1xipfdf"><img src="https://asciinema.org/a/9prjp6ub0lq6aio9nk1xipfdf.png" alt="Classic" width="400" border="0"></a>
###A passing test
<a href="https://asciinema.org/a/7qxe8m28lbqoqi8eew7j0eoss"><img src="https://asciinema.org/a/7qxe8m28lbqoqi8eew7j0eoss.png" alt="Classic" width="400" border="0"></a>
###A failing test
<a href="https://asciinema.org/a/350i28rmli5x66qs70flgkguq"><img src="https://asciinema.org/a/350i28rmli5x66qs70flgkguq.png" alt="Classic" width="400" border="0"></a>

##Quickstart
###Installation
Git Clone / Download the repo, ensure python v3.5 and pip are installed, then run the following command:

```
pip3.5 install tqdm blessings 
```
You can then invoke tamarin-tester with `./src/tamarin-tester.py`.If you wish to build tamarin-tester into a binary for ease of use, you can build the binary with pyinstaller:
```
pip3.5 install pyinstaller
pyinstaller src/tamarin-tester.py --onefile 
cp dist/tamarin-tester ~/.local/bin/tamarin-tester
```

###Building a benchmark
Firstly, we need to produce a benchmark file from a known-good build of tamarin,alternatively there are benchmarks created from the current master release of tamarin-prover in `data/benchmarks`
```
tamarin-tester TAMARIN -p PROTOCOLS --benchmark -maxproof FLOAT --maxcheck FLOAT
```
Where `TAMARIN` is the path to the known-good tamarin build you want to benchmark, on a standard install this is `~/.local/bin/tamarin-prover` and `PROTOCOLS` is the path to the directory of protocols you want to benchmark. Note this parameter is optional and will default to the current working directory if omitted. `--maxproof` and `--maxcheck` are mandatory are denote the maximum time in seconds to wait for tamarin-prover to terminate (for proving and well-formedness checks respectively).  `tamarin-tester` will then build the benchmark file and display its progress. The benchmark file will be output as `benchmark.res` in the same folder as the protcols. Benchmarking can take some time!

###Testing a new build
```
tamarin-tester TAMARIN -p PROTOCOLS -i BENCHMARK
```
Where `TAMARIN` is the path to the development tamarin build you want to test, `PROTOCOLS` is the path to the directory of protocols you want to test the tamarin build against.`BENCHMARK` is a path to the `benchmark.res` file you wish to test against. `PROTOCOLS` and `BENCHMARK` are optional, if omitted `tamarin-tester` will default respectively to the current working directory and the same directory as the protocols.

This will run the test and display a live progress report. Pay attention to the estimated time as testing can take some time. It will finish with a summary detailing one of `PASS`, `FAIL`, 'WARN' The first two are self-explanatory. 'WARN' is reported when their are protocol files in the directory which have no benchmark, when their are protocol files in the directory which have no lemmas (usually because of an `IFDEF`) or if the step counts change for a particular proof, but otherwise no actual failures occur.  

##Comand Line Options

###Both Modes (Mandatory)
This argument is mandatory in BOTH modes:

| Name | Description |
| --- |  --- | 
|TAMARIN_BINARY  | This argument is the path to the tamarin binary you wish to test/benchmark|

###Both Modes (Optional)
These arguments are optional and can be applied to both modes

| Name |Description |
| --- | --- | 
| -p PROTOCOL_DIR, --protocols PROTOCOL_DIR | The directory containing the protocols you wish to test/benchmark. The directory will be scanned recursively for all .spthy files. The default is to take the current working directory |
|  --flags FLAGS | User defined flags to pass to the tamarin binary, EVERY time it is invoked. See the README for how to set flags on a per-protocol basis|
|  -v, --verbose   |      Run in verbose mode|
|  --version        |    Print version information and exit|
| -h, --help        |    Print this help message|

###Test Mode (default):
This mode is selected by default 

| Name |Description |
| --- | --- | 
| -i BENCHMARK_FILE, --input BENCHMARK_FILE| By default tamarin-tester will look for a file named 'benchmark.res' located in the top level protocol directory. This option allows you to select a different file.|
| --contingency 2     |  When running a test for a protocol file. tamarin-tester will wait for the expected running time (in seconds) X the contingency factor. This is by default 2, but if you have benchmark file from a faster machine than this machine, you may need to raise it.|
| --overtime     |       This option is only applied if you also specify a max proof time and if passed will tell tamarin-tester to not test any protocols with an expected running time greater than the max proof time. These protocols will be reported as OVERTIME in the statistics rather than FAILED|

###Benchmark Mode:
This mode is selected by passing --benchmark

| Name |Description |
| --- | --- | 
|  --benchmark    |       This flag tells tamarin-tester to run in benchmark mode. Consequently it is mandatory to pass -mc and -mp flags detailed in the Timeout Arguments section below|
|  -o BENCHMARK_FILE, --output BENCHMARK_FILE| This is the location to write the benchmark file to after completion. By default it will be written to the top level of the protocols directory, named 'benchmark.res'|
| --repetitions 1     |  When calculating the average running time of a protocol, this is the number of samples to take. By default it is set to 1. If you need to benchmark on a machine with an unstable workload, setting it high will produce more reliable results at the cost of much greater execution time|

###Timeout Arguments:
These arguments are MANDATORY for BENCHMARK mode but OPTIONAL for TEST mode

| Name |Description |
| --- | --- | 
|  -mc FLOAT, --maxcheck FLOAT| Maximum time (in seconds) to run well-formedness check for. In TEST Mode, this is loaded from the file as the maximum running time of the protocols benchmarked, that are also in the protocol directory.|
| -mp FLOAT, --maxproof FLOAT| Maximum time (in seconds) to run a proof for. In TEST Mode, this is loaded from the file as the maximum running time of the protocols benchmarked that are also in the protocol directo when a max proof time has been specified, filter our protocols which are expected not to terminate. |

##Output

In benchmark mode: 

| Tag | Meaning |
| --- | --- |
| CHECK TIMEOUT | Checking well-formedness for the given protocol timed out (`maxcheck`) and it will be omitted from the benchmark |
| MALFORMED | The given protcol is not well-formed and it will be omitted from the benchmark |
| BENCH TIMEOUT | Tamarin did not terminate in the time specified (`maxproof`) and this protocol will be omitted from the benchmark|
| NO LEMMAS | This protocol did not contain any lemmas to prove, so there is nothing to benchmark, a flag may need to be passed to Tamarin to enable an `IFDEF`, alternatively you may annotate the protocol file with a line of the form: `#tamarin-tester-flags:FLAGS` which will lead to tamarin-tester passing through this flag to tamarin-prover only for this protocol file |

In test mode: 

| Tag | Meaning |
| --- | --- |
| PASSED | This protocol has identical lemma results and stepsizes under the new tamarin build as did under the benchmarked Tamarin build |
| WARNING | This protocol has identical lemma results (true/false) but there are minor differences e.g. stepsize |
| FAILED | The new Tamarin build disagress with the benchmarked build for one or more lemmas |
| NO LEMMAS | The benchmarked protocol had no lemmas and consequently there is nothing to compare |
| NO BENCHMARK | The protocol was in the protocols directory but not in the benchmark file and hence could not be checked |
| OVERTIME | The average runtime for this protocol is higher than the max allowed run time and hence it was expected to timeout, only occurs if the `--overtime` flag is passed. Otherwise these cases are treated as failures. |

For PASSED, WARNING, FAILED, there will be attached reason messages: 

| Tag | Meaning |
| --- | --- |
| STEPSIZE INC | This lemma took more steps to prove with the new build |
| STEPSIZE DEC | This lemma took less steps to prove with the new build|
| INCORRECT | This lemma has a different truth value with the new build |
| TIMEOUT | This protocol failed to terminate in the allotted time which is the contingency value (argument) c * avgRunTime (from the benchmark file) for the protocol file |

##Passing Flags to Tamarin
This can be done in one of two ways,  either flags can be passed to every protocol with the `--flags` argument, or alternativel you can write `#tamarin-tester-flags:` inside a protocol file followed by the flags you want to pass for that particular protocol. Typically this will be to pass a flag for tamarin to enable an IFDEF. If you wish for a protocl file to be tested multiple times with different flags, you will have to duplicate and edit each file. 

##Contact 
Dennis Jackson

Doctoral student

Computer Science Department

University of Oxford

dennis (dot) jackson (at) cs (dot) ox (dot) ac (dot) uk 
