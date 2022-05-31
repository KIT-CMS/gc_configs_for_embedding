#!/bin/bash
set -e
export XRD_LOGLEVEL="Info"
runtime_start=`date +%s`
ioinput_start=$(</sys/class/net/eth0/statistics/rx_bytes)
iooutput_start=$(</sys/class/net/eth0/statistics/tx_bytes)

/usr/bin/time -f "monitoring_metrics_start\nmetric_runtime: %e \nmetric_cputime: %U \nmetric_syscputime: %S\nmetric_cpuefficiency: %P\nmetric_memory: %M\nmetric_filesysteminputs: %I\nmetric_filesystemoutputs: %O" ./full_embedding.sh
## for the job runtime
runtime_end=`date +%s`
ioinput_end=$(</sys/class/net/eth0/statistics/rx_bytes)
iooutput_end=$(</sys/class/net/eth0/statistics/tx_bytes)
runtime=$((runtime_end-runtime_start))
ioinput=$((ioinput_end-ioinput_start))
iooutput=$((iooutput_end-iooutput_start))
## for the job cpu time

echo "metric_runtime_v2: ${runtime}"
echo "metric_diskusage: not_implemented"
echo "metric_ioinput: ${ioinput}"
echo "metric_iooutput: ${iooutput}"
echo "metric_outputsize: $(ls -sC merged.root | cut -d" " -f1)"
echo "metric_hostname: $(hostname)"
echo "monitoring_metrics_end"
echo " --------------"
