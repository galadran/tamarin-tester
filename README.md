#Tamarin-Tester

##Introduction
This project is a lightwight black box tester for the [Tamarin Prover](https://github.com/tamarin-prover/tamarin-prover)

It aims to support rapid development of the Tamarin Prover by allowing developers to regression test their builds with in a timely and clear manner. It allows for the benchmarking of a suite of protocols against a known-good build of Tamarin and then for development builds to be tested against this benchmark. 

The tool automatically tests the quickest to verify protocols first in order to establish as quickly as possible whether a build is suffering issues. Additionally users can pass in maximum limits on how long to wait before assuming Tamarin will not terminate. 

##In Action
###Benchmarking
<a href="https://asciinema.org/a/bty6vz7v4xfzf0j0etong4fbh"><img src="https://asciinema.org/a/bty6vz7v4xfzf0j0etong4fbh.png" alt="Classic" width="400" border="0"></a>
###A passing test
<a href="https://asciinema.org/a/eplydwh1w5hlxw6k7njq4ulsv"><img src="https://asciinema.org/a/eplydwh1w5hlxw6k7njq4ulsv" alt="Classic" width="400" border="0"></a>
###A failing test
<a href="https://asciinema.org/a/a4g4112qy7i95sl9rbko9kmxu"><img src="https://asciinema.org/a/a4g4112qy7i95sl9rbko9kmxu.png" alt="Classic" width="400" border="0"></a>

##Quickstart
###Installation
Git Clone / Download the repo, ensure python3 and pip3 are installed, then run the following commands

```
pip3 install tqdm blessings pyinstaller
pyinstaller src/tamarin-tester.py --onefile
```
If you wish to add the binary to your system path for convenience, it is suggested to put it in the same folder as default for the tamarin-prover. 
```
cp dist/tamarin-tester ~/.local/bin/tamarin-tester
```

An already built binary for 64-bit Ubuntu 16.04 is on the Releases page, but has only been tested on one machine. 

###Building a benchmark
Firstly, we need to produce a benchmark file from a known-good build of tamarin
```
tamarin-tester TAMARIN -p PROTOCOLS --benchmark -maxproof INT --maxcheck INT
```
Where `TAMARIN` is the path to the known-good tamarin build you want to benchmark, on a standard install this is `~/.local/bin/tamarin-prover` and `PROTOCOLS` is the path to the directory of protocols you want to benchmark. Note this parameter is optional and will default to the current working directory if omitted. `--maxproof` and `--maxcheck` are mandatory are denote the maximum time in seconds to wait for tamarin-prover to terminate (for proving and well-formedness checks respectively).  `tamarin-tester` will then build the benchmark file and display its progress. The benchmark file will be output as `benchmark.res` in the same folder as the protcols. Benchmarking can take some time!

###Testing a new build
```
tamarin-tester TAMARIN -p PROTOCOLS -i BENCHMARK
```
Where `TAMARIN` is the path to the development tamarin build you want to test, `PROTOCOLS` is the path to the directory of protocols you want to test the tamarin build against.`BENCHMARK` is a path to the `benchmark.res` file you wish to test against. `PROTOCOLS` and `BENCHMARK` are optional, if omitted `tamarin-tester` will default respectively to the current working directory and the same directory as the protocols.

This will run the test and display a live progress report. Pay attention to the estimated time as testing can take some time. It will finish with a summary detailing one of `PASS`, `FAIL`, `????`. The first two are self-explanatory. `????` is reported when their are protocol files in the directory which have no benchmark, when their are protocol files in the directory which have no lemmas (usually because of an `IFDEF`) or if the step counts change for a particular proof, but otherwise no actual failures occur.  

##Comand Line Options
The path to the Tamarin build you want to bench or test is mandatory. For benchmark mode, selected by passing `-b` or `--benchmark`:

| Long Option | Short Option | Default | Description
| --- | --- | --- | --- |
|--protocols | -p | Working Directory | The directory containing protocols you want to test/benchmark |
|--verbose | -v | FLAG | Runs tamarin-tester with additional log messages |
|--repetitions | -r | 1 | When running in benchmark mode, the number of samples to take to for the expected average runtime. WARNING `-r 2` will DOUBLE the runtime of `-r 1` |
|--maxproof | -mp | NA | Denotes the maximum time to wait for tamarin-prover to return a proof. Mandatory for benchmark mode |
|--maxcheck | -mc | NA | Denotes the maximum time to wait for tamarin-prover to return a well-formedness check. Mandatory for benchmark mode. |
|--output | -o | Protocols Directory | In Benchmark Mode, the path to write the benchmark to |

Otherwise, tamarin-tester runs in test mode: 

| Long Option | Short Option | Default | Description
| --- | --- | --- | --- |
|--protocols | -p | Working Directory | The directory containing protocols you want to test/benchmark |
|--verbose | -v | FLAG | Runs tamarin-tester with additional log messages |
|--contingency | -c | 2 | When running in test mode, tamarin-tester will wait for tamarin-prover to return a result in at most contingency * expected_runtime for a given protocol.| 
|--maxproof | -mp | NA | Denotes the maximum time to wait for tamarin-prover to return a proof. In Test mode this defaults to a value calculated from the benchmark file. |
|--maxcheck | -mc | NA | Denotes the maximum time to wait for tamarin-prover to return a well-formedness check. In this TESt mode this defaults to a value calculated from the benchmark file. |
|--input | -i | Protocols Directory | In Test Mode, the path to read the benchmark from |
|--overtime | -over | FLAG | In Test mode, when a max proof time has been specified, filter our protocols which are expected not to terminate. |  

##Output
In benchmark mode: 
| Tag | Meaning |
| --- | --- |
| CHECK TIMEOUT | Checking well-formedness for the given protocol timed out (`maxcheck`) and it will be omitted from the benchmark |
| MALFORMED | The given protcol is not well-formed and it will be omitted from the benchmark |
| BENCH TIMEOUT | Tamarin did not terminate in the time specified (`maxproof`) and this protocol will be omitted from the benchmark|
| NO LEMMAS | This protocol did not contain any lemmas to prove, so there is nothing to benchmark, a flag may need to be passed to Tamarin to enable an `IFDEF`, alternatively you may annotate the protocol file with a line of the form: `tamarin-tester-flags:FLAGS` which will lead to tamarin-tester passing through this flag to tamarin-prover only for this protocol file |
##Passing Flags to Tamarin

In test mode: 

| Tag | Meaning |
| --- | --- |
| PASSED | This protocol has identical lemma results and stepsizes under the new tamarin build as did under the benchmarked Tamarin build |
| WARNING | This protocol has identical lemma results (true/false) but there are minor differences e.g. stepsize |
| FAILED | The new Tamarin build disagress with the benchmarked build for one or more lemmas |
| NO LEMMAS | The benchmarked protocol had no lemmas and consequently there is nothing to compare |
| MISSING | The protocol was in the protocols directory but not in the benchmark file and hence could not be checked |
| OVERTIME | The average runtime for this protocol is higher than the max allowed run time and hence it was expected to timeout, only occurs if the `--overtime` flag is passed. Otherwise these cases are treated as failures. |

For PASSED, WARNING, FAILED, there will be attached reason messages: 

| Tag | Meaning |
| --- | --- |
| STEPSIZE INC | This lemma took more steps to prove with the new build |
| STEPSIZE DEC | This lemma took less steps to prove with the new build|
| INCORRECT | This lemma has a different truth value with the new build |
| TIMEOUT | This protocol failed to terminate in the allotted time which is the contingency value (argument) c * avgRunTime (from the benchmark file) for the protocol file |

##Contact 
Dennis Jackson
Doctoral student
Computer Science Department
University of Oxford
dennis (dot) jackson (at) cs (dot) ox (dot) ac (dot) uk 
