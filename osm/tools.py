#!/usr/bin/python2
import os, pickle, math, time

# Function to check whether the PM is in the local hosts list with IP
def host_existed_IP(lists, IP):
	for item in lists:
		if cmp(item.split()[1], IP) == 0: 
			return 1
		else: continue
	return 0

# Function to check whether the PM is in the local hosts list with ID
def host_existed_ID(lists, ID):
	for item in lists:
		if int(item.split()[0]) == ID: 
			return 1
		else: continue
	return 0

# Function to get the latest ID in the locak hosts list
def latest_ID(lists):
	IDs=[]
	for item in lists:
		IDs.append(int(item.split()[0]))
	return max(IDs)

# Function to get the corresponding ID for a PM with its IP from the locak hosts list
def find_ID_by_IP(lists, IP):
	for item in lists:
		if cmp(item.split()[1], IP) == 0: 
			return long(item.split()[0])
		else: continue

# Function to get the corresponding IP for a PM with its ID from the locak hosts list
def find_IP_by_ID(lists, ID):
	for item in lists:
		if int(item.split()[0]) == ID:
			return item.split()[1]
		else: continue

# Function to get infos from the configure file LMA.cfg
def get_config():
	# Get configurations for the configure file
	CFG_file = open('setconfig.cfg','r')
	configs = CFG_file.readlines()
	CFG_file.close()
	config_dic={}
	for config in configs:
		config = config.strip('\n')
		array = config.split('=')
		config_dic[array[0]] = array[1]
	return config_dic

# Function to modify a certain para in the configure file LMA.cfg
def modify_config(KEY, VALUE):
	config_dic = get_config()
	config_dic[KEY] = VALUE
	# Rewrite the config file with updated values
	CFG_file = open('setconfig.cfg','w')
	for k, v in config_dic.items():
		line = k + '=' + v + '\n'
		CFG_file.write(line)
	CFG_file.close()

# Function to check whether the VM candidate is already in the record file migration_candidates_hotspot.txt for PUSH strategy
def vm_existed(VM_ID):
	if not os.path.isfile('migration_candidates_hotspot.txt'):
		return 0
	fileHandel = open('migration_candidates_hotspot.txt', 'r')
	records = fileHandel.readlines()
	fileHandel.close()
	vm_ids=[]
	for record in records:
		record = record.strip('\n')
		array = record.split()
		vm_ids.append(array[0])
	for vm_id in vm_ids:
		if long(vm_id) == VM_ID: 
			return 1
	return 0

# Function to update the migration_candidates_hotspot.txt with new candidates for PUSH strategy
def update_candidates(VM_ID, PM_ID):
	fileHandel = open('migration_candidates_hotspot.txt', 'r')
	records = fileHandel.readlines()
	fileHandel.close()
	candidates={}
	for record in records:
		record = record.strip('\n')
		array = record.split()
		candidates[array[0]] = array[1]

	fileHandel = open('migration_candidates_hotspot.txt', 'w')
	for k, v in candidates.items():
		if long(k) == VM_ID:
			candidates[k]=':'.join(v, str(PM_ID))
		record = k + ' ' + v + '\n'
		fileHandel.write(record)
	fileHandel.close()

# Function to get measurement factors from received packets for MEASUREMENT
def calculate_measurement(FILE):
	if not os.path.isfile(FILE):
		print "no replys"

	else:
		# Get all info of PM_infos from a file
		fileHandel = open(FILE,'r')
		a = []
		traffic_bytes = []
		traffic_packets = []
		load_records = {}
		try:
			while True:
				pm_info = pickle.load(fileHandel)
				ai = pm_info.CPU_current/pm_info.CPU_max
				#print str(pm_info.ID), pm_info.CPU_current, str(pm_info.Traffic_Bytes), str(pm_info.Traffic_packets)
				load_records[str(pm_info.ID)] = pm_info.CPU_current
				a.append(ai)
				traffic_bytes.append(pm_info.Traffic_Bytes)
				traffic_packets.append(pm_info.Traffic_packets)
		except EOFError:
			fileHandel.close()

		sorted_load_records = sorted(load_records.items(), key=lambda d:d[0], reverse = False)
		print '*****************'
		print '| PM\tLoad\t|'
		for load_record in sorted_load_records:
			print '| %s\t%.4f\t|' % (load_record[0], load_record[1])
		print '*****************'

		fileHandel=open('testfile.txt', 'a')
		i = 1
		while(i<9):
			if load_records.has_key(str(i)):
				load = '%.4f\t' % load_records[str(i)]
			else:	load = 'NaN\t'
			fileHandel.write(load)
			i+=1
		fileHandel.write('\n')
		fileHandel.close()
		traffic_total_bytes = 0
		for tr in traffic_bytes:
			traffic_total_bytes += tr

		traffic_total_packets = 0
		for tr in traffic_packets:
			traffic_total_packets += tr

		p = []
		a_total = 0
		for ai in a:
			a_total = a_total +ai

		for ai in a:
			pi = ai/a_total
			p.append(pi)

		n = len(p)
		H_P = 0
		for pi in p:
			H_P = H_P + pi * (math.log10(pi))

		print 'Number of PMs:', n
		H_max = -math.log10(n)
		
		if H_max == 0:
			E_P = 1
		else:
			E_P = H_P/H_max
		NL = a_total/n
		print 'System performance: entropy =', E_P
		print 'Normalized load:', NL
		return (traffic_total_bytes, traffic_total_packets, E_P, NL)

# Function to get corresponding VM name with its ID in the localhost
def find_vm_name_by_id(ID):
	val = os.popen("./vm_list.py | sed -e 1d ")
	results = val.readlines()
	dic={}
	for result in results:
		array = result.split()
		dic[array[0]] = array[8].split(',')[0].split(':')[1]
	return dic[ID]


# Function to check whether VM is running with its ID in the localhost
def vm_local(ID):
	# Get configurations for the configure file
	config_dic=get_config()
	hypervisor = config_dic['HYPERVISOR']
	#if cmp(hypervisor.lower(), 'xen') == 0:
	#	val = os.popen("xm list | sed -e 1d ")
	if cmp(hypervisor.lower(), 'kvm') == 0:
		val = os.popen("virsh list | sed -e \"1,2d\" | sed /^$/d")
	else:
		print "Not available hypervisor, please specify kvm in setconfig.cfg"
		exit()
	results = val.readlines()
	dic=[]
	#if cmp(hypervisor.lower(), 'xen') == 0:
	#	for result in results:
	#		array = result.split()
	#		dic.append(array[1])
	#else:
	for result in results:
		array = result.split()
		dic.append(array[0])
	for vm_id in dic:
		if long(vm_id) == ID: 
			return 1
	return 0
	

