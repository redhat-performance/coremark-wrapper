# CoreMark CPU Benchmark Wrapper

## Description

This wrapper automates running the CoreMark CPU benchmark developed by EEMBC (Embedded Microprocessor Benchmark Consortium). CoreMark is a synthetic benchmark that measures the performance of central processing units (CPUs) used in embedded systems.

The wrapper provides:
- Automated execution across multiple thread counts and CPU configurations
- Support for powers-of-2 or incremental CPU scaling
- Result collection, processing, and verification
- CSV and JSON output formats
- System configuration metadata capture
- Integration with test_tools framework
- Optional Performance Co-Pilot (PCP) integration

## What the Script Does

The `coremark_run` script performs the following workflow:

1. **Environment Setup**:
   - Clones the test_tools-wrappers repository if not present (default: ~/test_tools)
   - Sources error codes and general setup utilities

2. **Package Installation**:
   - Installs required dependencies via package_tool (gcc, bc, numactl, make, etc.)
   - Dependencies are defined in coremark.json for different OS variants (RHEL, Ubuntu, SLES, Amazon Linux)

3. **Test Execution**:
   - Clones CoreMark from EEMBC GitHub repository (default version: v1.01)
   - Runs CoreMark benchmark with configurable parameters:
     - Single thread count (default: all CPUs)
     - Powers-of-2 CPU scaling (1, 2, 4, 8, ... CPUs)
     - Incremental CPU scaling (1, 1+n, 1+2n, ... CPUs)
   - Each iteration produces two runs (run1.log and run2.log)
   - Executes via make with MULTITHREAD and USE_PTHREAD flags

4. **Data Collection**:
   - Captures system configuration (CPU count, cores per socket, NUMA nodes, kernel version, memory)
   - Records CoreMark version information
   - Logs start and end timestamps for each test run

5. **Result Processing**:
   - Aggregates results from multiple runs and iterations
   - Generates CSV files with iteration, thread count, and IterationsPerSec metrics
   - Creates transposed JSON output for verification
   - Produces summary reports (when using single CPU count mode)

6. **Verification**:
   - Validates results against Pydantic schema (result_schema.py)
   - Ensures all iteration, thread, and IterationsPerSec values are greater than 0
   - Validates timestamp fields
   - Uses csv_to_json and verify_results from test_tools

7. **Output**:
   - Creates results directory in the coremark subdirectory
   - Saves all raw output files (run*log), processed CSV/JSON, and system metadata
   - Generates summary files (run1_summary, run2_summary) for single CPU count runs
   - Optionally saves PCP performance data
   - Archives results to configured storage location

## Dependencies

Location of underlying workload: https://github.com/eembc/coremark

Packages required: bc, numactl, perf, unzip, make, sed, gawk, gcc, git, zip

To run:
```
[root@hawkeye ~]# git clone https://github.com/redhat-performance/coremark-wrapper
[root@hawkeye ~]# coremark-wrapper/coremark/coremark_run
```

The script will automatically clone the CoreMark repository and run the benchmark using all available CPUs by default.

## The CoreMark Benchmark

CoreMark is a standardized CPU benchmark that measures:

1. **List Processing**: Searching and sorting operations on linked lists
2. **Matrix Manipulation**: Common matrix operations (addition, multiplication, etc.)
3. **State Machine**: Simulates processing of data streams
4. **CRC**: Cyclic redundancy check computation

The benchmark produces a single metric: **Iterations Per Second** - the number of times the entire workload can be completed per second. Higher values indicate better CPU performance.

CoreMark is designed to be:
- Portable across different architectures
- Representative of real-world embedded applications
- Resistant to compiler optimizations that might skew results
- Suitable for comparing different CPUs and compiler settings

## Results Schema

The wrapper validates results using a Pydantic schema that requires:
- **iteration**: Integer > 0 (iteration number)
- **threads**: Integer > 0 (number of threads used)
- **IterationsPerSec**: Float > 0 (benchmark score)
- **Start_Date**: Datetime (test start timestamp)
- **End_Date**: Datetime (test end timestamp)

## Output Files

The results directory contains:

- **results_coremark.csv**: CSV file with benchmark scores organized by iteration and thread count
- **results_coremark.json**: JSON version of results for verification
- **run1_iter=N_threads=M.log**: Raw output from first run of each configuration
- **run2_iter=N_threads=M.log**: Raw output from second run of each configuration
- **run1_summary** / **run2_summary**: Aggregated summary reports (for single CPU count mode)
- **test_results_report**: Simple pass/fail indicator
- **System metadata**: CPU info, memory, NUMA topology, kernel version
- **PCP data** (if --pcp option used): Performance Co-Pilot monitoring data

## Command-Line Options

```
Options
--commit <value>: Git commit to use. Default is the tag v1.01
--cpu_add <n>: Starting at CPU count of 1, add this number of CPUs to each run.
    Cannot be used with --powers_2
--powers_2: Starting at 1, run the number of CPUs by powers of 2 (1, 2, 4, 8, ...).
    Cannot be used with --cpu_add
--tools_git <value>: Git repo to retrieve the required tools from.
    Default is https://github.com/redhat-performance/test_tools-wrappers

General options
  --home_parent <value>: Our parent home directory. If not set, defaults to current working directory.
  --host_config <value>: Default is the current host name.
  --iterations <value>: Number of times to run the test, defaults to 1.
  --pcp: Enable Performance Co-Pilot monitoring during the run.
  --run_user: User that is actually running the test on the test system. Defaults to user running wrapper.
  --sys_type: Type of system working with, aws, azure, hostname. Defaults to hostname.
  --sysname: Name of the system running, used in determining config files. Defaults to hostname.
  --tuned_setting: Used in naming the tar file, default for RHEL is the current active tuned. For non-RHEL systems, default is none.
  --usage: This usage message.
```

## Examples

### Basic run with defaults
```bash
./coremark_run
```
This runs with:
- Default 1 iteration
- All available CPUs
- CoreMark version v1.01
- Two runs per iteration (run1.log and run2.log)

### Run with powers-of-2 CPU scaling
```bash
./coremark_run --powers_2
```
Tests CPU configurations at 1, 2, 4, 8, 16, ... up to the maximum number of CPUs available. This explores scaling characteristics across different levels of parallelism.

### Run with incremental CPU addition
```bash
./coremark_run --cpu_add 4
```
Tests CPU configurations at 1, 5, 9, 13, ... incrementing by 4 CPUs each time up to the maximum available.

### Run with specific CoreMark version
```bash
./coremark_run --commit <git-commit-hash>
```
Clones the full CoreMark repository and checks out a specific commit instead of using the default v1.01 tag.

### Run multiple iterations
```bash
./coremark_run --iterations 5
```
Runs the benchmark 5 times to get more consistent results and identify variance.

### Run with PCP monitoring
```bash
./coremark_run --pcp
```
Collects Performance Co-Pilot data during the run for detailed performance analysis.

### Combined: Multi-CPU scaling with multiple iterations
```bash
./coremark_run --powers_2 --iterations 3 --pcp
```
Runs 3 iterations across powers-of-2 CPU counts with PCP monitoring enabled.

## How CPU Scaling Works

The script supports three modes of CPU configuration:

### 1. Single CPU Count (Default)
By default, the benchmark runs once using all available CPUs on the system.

### 2. Powers-of-2 Scaling (`--powers_2`)
Tests CPU counts in powers of 2:
- Starts at 1 CPU
- Doubles each iteration: 1, 2, 4, 8, 16, 32, ...
- Continues until reaching maximum CPU count
- Always includes a final run with all CPUs

Example: On a 48-CPU system: 1, 2, 4, 8, 16, 32, 48 CPUs

### 3. Incremental Scaling (`--cpu_add N`)
Tests CPU counts with fixed increments:
- Starts at 1 CPU
- Adds N CPUs each iteration: 1, 1+N, 1+2N, ...
- Continues until reaching maximum CPU count
- Always includes a final run with all CPUs

Example: With `--cpu_add 8` on a 48-CPU system: 1, 9, 17, 25, 33, 41, 48 CPUs

**Note**: You cannot use both `--powers_2` and `--cpu_add` simultaneously.

## Integration with test_tools

The wrapper integrates with the test_tools-wrappers framework:

- **csv_to_json**: Converts results to JSON format
- **gather_data**: Collects system information
- **general_setup**: Parses common options, handles tuned profile detection
- **move_data**: Organizes output files
- **package_tool**: Installs required packages
- **save_results**: Archives results to configured storage
- **test_header_info**: Generates CSV headers with system metadata
- **verify_results**: Validates against Pydantic schema

## Return Codes

The script uses standardized error codes from test_tools error_codes:
- **E_SUCCESS (0)**: Success
- **101**: Git clone failure
- **E_GENERAL**: General execution errors (validation failures, test execution failures)
- **E_USAGE**: Invalid command-line options

Exit codes indicate specific failure points for automated testing workflows.

## Notes

- CoreMark produces two runs per iteration to verify consistency
- Results vary based on system load, so multiple iterations are recommended for stable measurements
- The benchmark is designed to stress CPU performance, not memory bandwidth
- Thread scaling behavior depends on CPU architecture (SMT/hyperthreading, cache hierarchy, etc.)
- Official CoreMark results require specific validation and reporting procedures (see EEMBC CoreMark rules)
- This wrapper is designed for performance testing and comparison, not for submitting official scores
