# CoreMark Benchmark Wrapper

## Description

This wrapper facilitates the automated execution of the CoreMark benchmark. CoreMark is an industry-standard benchmark for evaluating embedded processor core performance, measuring throughput in Iterations/Sec by executing a set of core algorithms (list processing, matrix manipulation, state machine, and CRC).

The wrapper provides:
- Automated CoreMark download, build, and execution.
- Configurable CPU thread scaling (linear increment or powers of 2).
- Multi-threaded execution using POSIX threads.
- Support for x86_64 (AMD/Intel) and aarch64 (ARM) architectures.
- Result collection, processing, and verification.
- CSV and JSON output formats.
- System configuration metadata capture.
- Integration with test_tools framework.
- Optional Performance Co-Pilot (PCP) integration.

## Command-Line Options

```
CoreMark Options:
  --commit <n>: Git commit or tag to use. Default is v1.01.
  --cpu_add <n>: Starting at CPU count of 1, add this number of CPUs to each run.
      Useful for linear thread scaling tests (e.g., --cpu_add 4 runs at 1, 5, 9, ... up to max CPUs).
  --powers_2: Starting at 1, run the number of CPUs by powers of 2.
      Runs at 1, 2, 4, 8, 16, ... up to max CPUs.
      Cannot be used together with --cpu_add.

General test_tools options:
  --home_parent <value>: Parent home directory. If not set, defaults to current working directory.
  --host_config <value>: Host configuration name, defaults to current hostname.
  --iterations <value>: Number of times to run the test, defaults to 1.
  --run_label <value>: Label to associate with the pbench run. No default setting.
  --run_user: User that is actually running the test on the test system. Defaults to current user.
  --sys_type: Type of system working with (aws, azure, hostname). Defaults to hostname.
  --sysname: Name of the system running, used in determining config files. Defaults to hostname.
  --tuned_setting: Used in naming the results directory. For RHEL, defaults to current active tuned profile.
      For non-RHEL systems, defaults to 'none'.
  --use_pcp: Enable Performance Co-Pilot monitoring during test execution.
  --tools_git <value>: Git repo to retrieve the required tools from.
      Default: https://github.com/redhat-performance/test_tools-wrappers
  --no_pkg_install: Skip package installation (don't use dnf/yum/apt).
  --pbench: Run via pbench-user-benchmark.
  --json_skip: Skip JSON conversion of CSV results.
  --verify_skip: Skip result verification against schema.
  --usage: Display usage information.
```

## What the Script Does

The `coremark_run` script performs the following workflow:

1. **Environment Setup**:
   - Clones the test_tools-wrappers repository if not present (default: `$curdir/test_tools`).
   - Sources general setup utilities for system detection and configuration.
   - Gathers hardware information via `gather_data`.

2. **Package Installation**:
   - Installs required dependencies via package_tool (bc, gcc, make, git, etc.).
   - Dependencies are defined in coremark.json for different OS variants (RHEL, Ubuntu, SLES, Amazon Linux).
   - Can be skipped with `--no_pkg_install`.

3. **CoreMark Download**:
   - Clones the CoreMark repository from eembc/coremark.
   - By default, clones at tag `v1.01` using a shallow clone (`--depth 1`).
   - If `--commit` is specified, performs a full clone and checks out the requested commit or tag.
   - If CoreMark was previously cloned, reuses the existing directory and archives old results.

4. **Result Archival**:
   - If a previous results directory exists, archives old logs, results CSV, and test report into a timestamped `archive_YYYY.MM.DD-HH.MM.SS` directory before starting new runs.

5. **Test Execution**:
   - Detects the number of available CPUs via `nproc`.
   - Runs CoreMark for the specified number of iterations (`--iterations`, default 1).
   - Thread scaling modes:
     - **Default**: Runs at maximum CPU count only.
     - **Powers of 2** (`--powers_2`): Runs at 1, 2, 4, 8, ... up to max CPUs.
     - **Linear increment** (`--cpu_add N`): Runs at 1, 1+N, 1+2N, ... up to max CPUs.
   - In all scaling modes, a final run at the exact max CPU count is always included.
   - Before each build, source files are touched to force recompilation with the new thread count.
   - CoreMark is compiled with POSIX thread support: `-DMULTITHREAD=<threads> -DUSE_PTHREAD -pthread`.
   - On Ubuntu, sets `PORT_DIR=linux64` for CoreMark compilation.
   - Raw output logs are renamed to `run1_iter=N_threads=M.log` and `run2_iter=N_threads=M.log`.

6. **PCP Integration (Optional)**:
   - If `--use_pcp` is specified, starts Performance Co-Pilot logging before test execution.
   - Captures per-iteration performance data (`iterations_sec` metric) into PCP archives.
   - Stops PCP logging after all iterations complete.
   - PCP data is saved to a timestamped `/tmp/pcp_YYYY.MM.DD-HH.MM.SS` directory.

7. **Data Collection**:
   - Captures system configuration (hostname, CPU family, memory, NUMA nodes, kernel version, tuned profile).
   - Writes metadata as headers in the results CSV via `test_header_info`.

8. **Result Processing**:
   - Extracts `Iterations/Sec` from each run log.
   - Generates CSV files with configuration and performance data.
   - Creates JSON output for verification.
   - Produces summary reports (`run1_summary`, `run2_summary`) with averaged metrics when running at a single thread count.

9. **Verification**:
   - Validates results against Pydantic schema (result_schema.py).
   - Ensures all required fields (`iteration`, `threads`, `IterationsPerSec`) are present and valid.
   - Uses csv_to_json and verify_results from test_tools.

10. **Output**:
    - Saves results via `save_results` to the configured home directory (`/${to_home_root}/${to_user}`).
    - Includes all raw log files, summaries, `test_results_report`, results CSV, and optionally PCP data.

## Dependencies

Location of underlying workload: Downloaded from https://github.com/eembc/coremark.

**General packages required**: gcc, make, bc, git, zip, unzip, numactl, sed, gawk

**Additional OS-specific packages**:
- **RHEL**: perf.
- **Ubuntu**: (no additional packages).
- **Amazon Linux**: perf.
- **SLES**: libnuma1 (replaces numactl), perf.

Dependencies are automatically installed via `package_tool` unless `--no_pkg_install` is specified.

To run:
```bash
git clone https://github.com/redhat-performance/coremark-wrapper
cd coremark-wrapper/coremark
./coremark_run
```

The script will automatically detect your CPU architecture and select appropriate defaults.

## The CoreMark Benchmark

CoreMark is a benchmark that exercises common embedded processor operations:

**List Processing, Matrix Manipulation, State Machine, and CRC**

Where:
- **List Processing** tests pointer-chasing and data-dependent branching
- **Matrix Manipulation** tests array indexing and multiply-accumulate operations
- **State Machine** tests branch prediction and switch-case handling
- **CRC** (Cyclic Redundancy Check) tests bitwise and table-lookup operations

### Key CoreMark Parameters

1. **Threads**: The number of POSIX threads used for parallel execution. This wrapper supports running at maximum CPU count, powers of 2, or linear increments. More threads test multi-core scaling behavior.

2. **Iterations**: CoreMark runs its core algorithms in a loop. The number of loop iterations is automatically calibrated to ensure the benchmark runs for at least 10 seconds, producing a stable measurement.

3. **Performance Metric**: CoreMark reports performance in **Iterations/Sec** (iterations of the core algorithm suite completed per second). Higher values indicate better performance.

## Output Files

The results directory contains:

- **results_coremark.csv**: CSV file with system metadata headers and CoreMark performance metrics
- **results_coremark.json**: JSON conversion of CSV results for verification
- **run1_iter=N_threads=M.log** / **run2_iter=N_threads=M.log**: Raw output files from CoreMark runs showing detailed results
- **run1_summary** / **run2_summary**: Aggregated metrics averaged across iterations
- **test_results_report**: Overall test status ("Ran" or "Failed")
- **meta_data.yml\***: System metadata (CPU info, memory, NUMA topology, kernel version)
- **PCP data** (if --use_pcp option used): Performance Co-Pilot monitoring data

## Examples

### Basic run with defaults
```bash
./coremark_run
```
This runs with:
- Maximum CPU thread count
- 1 iteration
- No thread scaling

### Run multiple iterations
```bash
./coremark_run --iterations 3
```
Runs the benchmark 3 times to check consistency.

### Thread scaling with powers of 2
```bash
./coremark_run --powers_2
```
Runs CoreMark at 1, 2, 4, 8, ... up to max CPUs.

### Thread scaling with linear increment
```bash
./coremark_run --cpu_add 4
```
Runs CoreMark at 1, 5, 9, 13, ... up to max CPUs.

### Run with a specific CoreMark commit
```bash
./coremark_run --commit v1.0
```
Uses the specified CoreMark git tag or commit instead of the default (v1.01).

### Run with PCP monitoring
```bash
./coremark_run --use_pcp
```
Collects Performance Co-Pilot data during the run.

### Skip package installation
```bash
./coremark_run --no_pkg_install
```
Skips automatic dependency installation (useful if packages are already installed).

### Combination example
```bash
./coremark_run --powers_2 --iterations 3 --use_pcp
```
Runs with powers-of-2 thread scaling, 3 iterations, and collects PCP data.

## How Thread Scaling Works

The script supports multiple modes for scaling across CPU thread counts:

### Default (No Scaling)
Runs CoreMark once at the maximum CPU count detected by `nproc`. This is the simplest mode for measuring peak multi-threaded throughput.

### Powers of 2 (`--powers_2`)
1. Starts at 1 thread.
2. Doubles the thread count each step: 1, 2, 4, 8, 16, ...
3. Continues until reaching or exceeding the maximum CPU count.
4. Always includes a final run at the exact max CPU count.

### Linear Increment (`--cpu_add N`)
1. Starts at 1 thread.
2. Adds N threads each step: 1, 1+N, 1+2N, 1+3N, ...
3. Continues until reaching or exceeding the maximum CPU count.
4. Always includes a final run at the exact max CPU count.

### Build Process
CoreMark is compiled with POSIX thread support. For each thread count, the wrapper:
- Touches source files to force recompilation.
- Sets `-DMULTITHREAD=<threads>` for the target thread count.
- Sets `-DUSE_PTHREAD` and `-pthread` for POSIX thread linking.
- On Ubuntu, sets `PORT_DIR=linux64` for CoreMark compilation.

### Mutual Exclusivity
`--powers_2` and `--cpu_add` cannot be used together. The script exits with an error if both are specified.

## Return Codes

- **0**: Success.
- **1**: General execution errors (git clone failure, build failure, invalid arguments, checkout failure).

Specific failure conditions:
- Git clone of CoreMark repository fails.
- `make` compilation fails.
- Both `--cpu_add` and `--powers_2` specified simultaneously.
- Git checkout of custom `--commit` value fails.

## Notes

### Architecture Support
- **x86_64**: Full support for AMD and Intel CPUs.
- **aarch64**: Full support for ARM CPUs.

### OS-Specific Behavior
- **Ubuntu**: Uses `linux64` port directory for CoreMark compilation.
- **RHEL**: Automatically detects and uses active tuned profile.
- **SLES**: Supported with SUSE-specific package names.

### Special Cases
- **Ubuntu**: Requires `PORT_DIR=linux64` to be set for CoreMark compilation.
- **Previous Results**: Automatically archived into timestamped `archive_YYYY.MM.DD-HH.MM.SS` directories before new runs.

### Performance Tips
- Run multiple iterations to verify consistency.
- Ensure system is idle (no other workloads) for best results.
- Use `--powers_2` or `--cpu_add` to characterize thread scaling behavior.
- Consider the active tuned profile on RHEL systems.
- Use `--use_pcp` to collect detailed performance counters for analysis.

### Troubleshooting
- If CoreMark fails to build, verify that `gcc` and `make` are installed.
- If results show unexpected performance, check CPU frequency and system load.
- Use `--use_pcp` to collect performance counters for deeper analysis.
- Previous results are automatically archived with a timestamp before new runs.
