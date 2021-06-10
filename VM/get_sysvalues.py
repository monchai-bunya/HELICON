#!/usr/bin/python2
import os, multiprocessing, subprocess, platform, re, time
from sys_tools import load_stat, memory_stat, net_stat, cpu_core, vcpu, cpu_clock, get_ping_time

#get first value for bandwidth
net = net_stat('wlp2s0')
start_time = time.time()
bytes_sum1 = net['ReceiveBytes'] + net['TransmitBytes']

#calculate load
load = load_stat()

#calculate memoey
mems = memory_stat()
mem_utilization = (mems['MemUsed']/mems['MemTotal'])*100

#calculate core number
core = cpu_core()

#calculate vcpu number
vcpu = vcpu()

#calculate cpu clock and cache
clock_sp, cache_sz = cpu_clock()

#calculate latency, packet loass, jitter
ping_tm,pac_ls,jit = get_ping_time('127.0.0.1')

#get second value for bandwidth and get band width
net = net_stat('wlp2s0')
end_time = time.time()
bytes_sum2 = net['ReceiveBytes'] + net['TransmitBytes']
bytes_diff = bytes_sum2 - bytes_sum1
measure_time = end_time-start_time
bandwidth = bytes_diff/measure_time

#print(load['lavg_5'])
#print(mems['MemTotal'])
#print(net['ReceiveBytes'])
#print(net['TransmitBytes'])
#print(core)
#print(vcpu)
#print(clock_sp)
#print(cache_sz)
#print(ping_tm)
#print(pac_ls)
#print(jit)
#print(bandwidth)
print(mem_utilization)
