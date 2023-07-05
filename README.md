Automation wrapper for coremark

Description: CoreMark's primary goals are simplicity and providing a method for
             testing only a processor's core features. For more information see
	     https://github.com/eembc/coremark/blob/main/README.md
  
Location of underlying workload:  https://github.com/eembc/coremark

Packages required: bc,numactl

To run:
[root@hawkeye ~]# git clone https://github.com/redhat-performance/coremark-wrapper
[root@hawkeye ~]# coremark-wrapper/coremark/coremark_run


Options
```
  --commit <n>: git commit to use, default is the tag v1.01
  --cpu_add <n>: starting at cpu count of 1, add this number of cpus to each run
  --powers_2s: starting at 1, run the number of cpus by powers of 2's
General options
  --home_parent <value>: Our parent home directory.  If not set, defaults to current working directory.
  --host_config <value>: default is the current host name.
  --iterations <value>: Number of times to run the test, defaults to 1.
  --pbench: use pbench-user-benchmark and place information into pbench, defaults to do not use.
  --pbench_user <value>: user who started everything. Defaults to the current user.
  --pbench_copy: Copy the pbench data, not move it.
  --pbench_stats: What stats to gather. Defaults to all stats.
  --run_label: the label to associate with the pbench run. No default setting.
  --run_user: user that is actually running the test on the test system. Defaults to user running wrapper.
  --sys_type: Type of system working with, aws, azure, hostname.  Defaults to hostname.
  --sysname: name of the system running, used in determing config files.  Defaults to hostname.
  --tuned_setting: used in naming the tar file, default for RHEL is the current active tuned.  For non
    RHEL systems, default is none.
  --usage: this usage message.
```

Note: The script does not install pbench for you.  You need to do that manually.
