#!/usr/bin/python2
import os, multiprocessing, subprocess, platform, re, time
from sys_tools import load_stat, memory_stat, net_stat, cpu_core, vcpu, cpu_clock, get_ping_time
from tools import get_config, modify_config

while True:

   #get values from config file
   config_dic = get_config()
   outfile = config_dic['VNFRS_FILENAME']
   outfileml = config_dic['VNFRS_FILENAME_ML']
   mvout = 'mv outtemprs.csv ' + outfile
   mvoutml = 'mv outtemprsml.csv ' + outfileml

   #open file and write header
   tcap = open('outtemprs.csv','w')
   tcapml = open('outtemprsml.csv','w')
   # raspi 11, vnf = 21, ue = 31
   tcap.write('device_type')
   tcap.write(',')
   tcap.write('normalized_load')
   tcap.write(',')
   tcap.write('memtotal')
   tcap.write(',')
   tcap.write('mem_utilization')
   tcap.write(',')
   tcap.write('core_number')
   tcap.write(',')
   tcap.write('vcpu_number')
   tcap.write(',')
   tcap.write('cpu_speed')
   tcap.write(',')
   tcap.write('cache_size')
   tcap.write(',')
   tcap.write('latency')
   tcap.write(',')
   tcap.write('packet_loss')
   tcap.write(',')
   tcap.write('jitter')
   tcap.write(',')
   tcap.write('bandwidth')
   tcap.write(',')
   tcap.write('net_utilization')
   tcap.write(',')
   tcap.write('IP')
   tcap.write('\n')

   #write header
   tcapml.write('normalized_load')
   tcapml.write(',')
   tcapml.write('mem_utilization')
   tcapml.write(',')
   tcapml.write('vcpu_number')
   tcapml.write(',')
   tcapml.write('latency')
   tcapml.write(',')
   tcapml.write('packet_loss')
   tcapml.write(',')
   tcapml.write('jitter')
   tcapml.write(',')
   tcapml.write('bandwidth')
   tcapml.write(',')
   tcapml.write('net_utilization')
   tcapml.write(',')
   tcapml.write('IP')
   tcapml.write(',')
   tcapml.write('device_type')
   tcapml.write('\n')

   #get first value for bandwidth
   net = net_stat(config_dic['NET_INTERFACE'])
   start_time = time.time()
   bytes_sum1 = net['ReceiveBytes'] + net['TransmitBytes']
   time.sleep(1)
   #calculate core number
   core = cpu_core()

   #calculate load
   load = load_stat()
   norm_load = float(load['lavg_5'])/core
 
   #calculate memoey
   mems = memory_stat()
   mem_utilization = (mems['MemUsed']/mems['MemTotal'])*100

   #calculate vcpu number
   vcpu_num = vcpu()

   #calculate cpu clock and cache
   clock_sp, cache_sz = cpu_clock()

   #get second value for bandwidth and get band width
   net = net_stat(config_dic['NET_INTERFACE'])
   end_time = time.time()
   bytes_sum2 = net['ReceiveBytes'] + net['TransmitBytes']
   bytes_diff = bytes_sum2 - bytes_sum1
   measure_time = end_time-start_time
   bandwidth = bytes_diff/measure_time/125000
   net_utilization = (bandwidth/float(config_dic['LINK_CAPACITY']))*100
   
   addresses = config_dic['PING_ADDRESS_RS']
   ad = addresses.split(',')
   for i in ad:
      #calculate latency, packet loass, jitter
      ping_tm,pac_ls,jit = get_ping_time(i) 

      #save all data for backup  
      tcap.write(str(config_dic['DEVICE_TYPE']))
      tcap.write(',')
      tcap.write(str(norm_load))
      tcap.write(',')
      tcap.write(str(mems['MemTotal']))
      tcap.write(',')
      tcap.write(str(mem_utilization))
      tcap.write(',')
      tcap.write(str(core))
      tcap.write(',')
      tcap.write(str(vcpu_num))
      tcap.write(',')
      tcap.write(str(clock_sp))
      tcap.write(',')
      tcap.write(str(cache_sz))
      tcap.write(',')
      tcap.write(str(ping_tm))
      tcap.write(',')
      tcap.write(str(pac_ls))
      tcap.write(',')
      tcap.write(str(jit))
      tcap.write(',')
      tcap.write(str(bandwidth))
      tcap.write(',')
      tcap.write(str(net_utilization))
      tcap.write(',')
      tcap.write(i)
      tcap.write('\n')
    
      #write to file for ML
      tcapml.write(str(norm_load))
      tcapml.write(',')
      tcapml.write(str(mem_utilization))
      tcapml.write(',')
      tcapml.write(str(vcpu_num))
      tcapml.write(',')
      tcapml.write(str(ping_tm))
      tcapml.write(',')
      tcapml.write(str(pac_ls))
      tcapml.write(',')
      tcapml.write(str(jit))
      tcapml.write(',')
      tcapml.write(str(bandwidth))
      tcapml.write(',')
      tcapml.write(str(net_utilization))
      tcapml.write(',')
      tcapml.write(i)
      tcapml.write(',')
      tcapml.write(str(config_dic['DEVICE_TYPE']))
      tcapml.write('\n')
  
   tcap.close()
   tcapml.close()	
   os.system(mvout)  
   os.system(mvoutml) 
   time.sleep(10)


