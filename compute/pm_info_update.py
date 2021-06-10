#!/usr/bin/python2
import time, sys, os
from sys_tools import load_stat, memory_stat, get_ping_time  #, load_pm_xen
from tools import get_config

# Get configurations for the configure file
config_dic=get_config()
#if cmp(config_dic["HYPERVISOR"].lower(), 'xen') == 0: hypervisor=0
if cmp(config_dic["HYPERVISOR"].lower(), 'kvm') == 0: hypervisor=1
else: 
	print "Hypervisor not available."
	exit()

k=5
load_sum = 0

while(k>0):
	#if hypervisor == 0:
	#	load_sum += float(load_pm_xen()['lavg_5'])
	#else: 
	load_sum += float(load_stat()['lavg_5'])
	k -= 1

L_t = load_sum/5
#if hypervisor == 0:
#	l_t = float(load_pm_xen()['lavg_5'])
#else: 
l_t = float(load_stat()['lavg_5'])

while True:
	L_t = 0.2*l_t + 0.8*L_t
	#if hypervisor == 0:
        #	l_t = float(load_pm_xen()['lavg_5'])
	#else: 
	l_t = float(load_stat()['lavg_5'])
	string = '%s %s' % (L_t, l_t)
	fileHandel = open('pm_info_n.txt', 'w')
	fileHandel.write(string)
	fileHandel.close()
	fileHandel2 = open('pm_info_list.csv', 'a')
	fileHandel2.write(str(L_t))
	fileHandel2.write('\n')
	fileHandel2.close()

	ping_time, packet_loss, jitter = get_ping_time('192.168.40.4')
	tcap2 = open('latency_list.csv','a')
	cap2 = open('latency_request.txt','w')
	tcap2.write(str(ping_time))
	tcap2.write('\n')
	cap2.write(str(ping_time))
	tcap2.close()
	cap2.close()	
	os.system('mv pm_info_n.txt pm_info.txt')
	time.sleep(1)
