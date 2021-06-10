#!/usr/bin/python2  

# Monitor the load to trigger push and pull strategies
import os, sys, time, thread, pickle, random, LMA_measurement, math, csv
from sys_tools import load_stat, memory_stat
from tools import get_config, modify_config, calculate_measurement, find_ID_by_IP, find_IP_by_ID
from os import path

# Function for calculating the cost for candidates based on cost model
def calculate_cost(V_mem, D):
	V = {}
	T = {}
	W = {}
	T_down = 0

	R =  100.0 # unit: MB/s
	V_thd = 0.25 # unit: MB 256 kB
	T_resume = 0.02    # unit: s
	a = -0.0463
	b = -0.0001
	c = 0.3586

	V[0] = V_mem

	D_R = D/R
	if D_R==0:
		n=0
	else:
		n = math.log10(V_thd/V_mem)/math.log10(D_R)
	n = int (n) + 1

	for i in range(0, n+1):
		T[i] = V[i]/R
		gama = a * T[i] + b * D + c
		W[i+1] = gama * T[i] *D
		V[i+1] = T[i] * D - W[i+1]
		if V[i+1] <= V_thd or V[i+1] > V[i]:
			V[i+1] = T[i] *D
			T[i+1] = V[i+1]/R
			T_down = T[i+1] + T_resume
			break

	V_mig = 0
	T_mig = 0

	for k, V_i in V.items():
		V_mig += V_i

	for k, T_i in T.items():
		T_mig += T_i

	return (V_mig, T_mig + T_down)

# Function for calculating the entropy for each PM 
def calculate_entropy(pm_infos, pm_source, pm_destination, vm_load):
	print "vm load:", vm_load
	a = []
	for id, pm_info in pm_infos.items():
		EWMA_pm_load = 0.2 * pm_info.CPU_record + 0.8 * pm_info.CPU_current
		if cmp(id, pm_destination) == 0:
			EWMA_pm_load += vm_load
		if cmp(id, pm_source) == 0:
			print 'pm_source', id
			EWMA_pm_load -= vm_load
		ai = EWMA_pm_load/pm_info.CPU_max
		print id, ai
		a.append(ai)

	p = []
	a_total = 0
	for ai in a:
		a_total = a_total +ai

	for ai in a:
		pi = ai/a_total
		p.append(pi)

	n = len(p)
	H_P = 0
	try:
		for pi in p:
			H_P = H_P + pi * (math.log10(pi))
	except ValueError:
		H_P = 0
	H_max = -math.log10(n)

	return H_P/H_max

# Function to decide the winner of the auction for PUSH strategy
def decide_winner(request_number,state,eps,expect,load,w_time,w_load):
	state_number = request_number
	state = state
	epsilon = eps
	accept_delay = expect
	vm_load = load
	weight_time = w_time
	weight_load = w_load
	time.sleep(2)
	global TEST
	VM_CANDIDATES ={}
	VM_candidates_load = {}
	VM_candidates_cost = {}
	PM_infos = {}
	vm_ids=[]
	vm_loads=[]
	vm_migrate = [100]*4
	placement = [100]*4
	predicted_t = [100]*4
	source = [100]*4
	EWMA_pm_load = [0]*4
	core = [0]*4
	save_foldert = './result_ttotal/'
	node_select = save_foldert + "node_select.txt"
	save_folders = './result_scalarized/'
	scala_node_select = save_folders + "scala-node_select.txt"
	save_folder = './result_load/'
	load_node_select = save_folder + "load_node_select.txt"
	load_accumulatenpy = save_folder + "load_accumulate.txt"
	if state == 1:
	  load_accumulate_ad = [0]*4
	  #print 'load 1'
	else:
	  if path.exists(load_accumulatenpy):
	    with open(load_accumulatenpy,'rb') as fp:
		load_accumulate_ad = pickle.load(fp)
		#print 'load 2'
	  else:
	    load_accumulate_ad = [0]*4
	    #print 'load 3'
	'''
	print state_number
	print epsilon
	command = './multiarms.py ' + str(state_number) + ' ' + str(state) + ' ' + str(epsilon) + ' ' + accept_delay + ' 0.45 0.45 0.53 0.57'
	if TEST == 1: 
		print command
	os.system(command)
	'''
	# No candidates, multicast RESOURCE RELEASE, and backoff
	if not os.path.isfile('VM_candidates_hotspot.txt'):
		print "No reply -> multicast Resource Release message"
		# Multicast RESOURCE RELEASE message
		command = './send.py 9'
		if TEST == 1: 
			print command
		os.system(command)

	else:
		# Get all info of VM_candidates from a file
		fileHandel = open('VM_candidates_hotspot.txt','r')
		try:
			while True:
				vm_info = pickle.load(fileHandel)
				# calculate the EWMA for each VM's load
				try:
					#VM_candidates_cost[str(vm_info.ID)] = calculate_cost(vm_info.MEM, vm_info.Page_dirty_rate)
					VM_candidates_load[str(vm_info.ID)] = 0.2 * float(vm_info.CPU_record) + 0.8 * float(vm_info.CPU_current)
				except ValueError:
					#print 'Dirtying rate:', vm_info.Page_dirty_rate, 'Value error, continue'
					continue
		except EOFError:
			fileHandel.close()

		# Get all info of PM_candidates from a file
		fileHandel2 = open('PM_candidates_hotspot.txt','r')
		try:
			while True:
				pm_info = pickle.load(fileHandel2)
				PM_infos[str(pm_info.ID)] = pm_info
				#for id, p_info in PM_infos.items():
				#	print id
				#	EWMA_pm_load[int(id)] = (0.2 * p_info.CPU_record + 0.8 * p_info.CPU_current)/p_info.CPU_max
		except EOFError:
			fileHandel2.close()
		for id, pm_info in PM_infos.items():
			#print id
			EWMA_pm_load[int(id)-1] = (0.2 * pm_info.CPU_record + 0.8 * pm_info.CPU_current)/pm_info.CPU_max
			core[int(id)-1] = pm_info.CPU_max

		#print EWMA_pm_load
		#print core
		# The case that the VM_candidates list is empty
		if len(VM_candidates_load) == 0: 
			print "multicast Resource Release message"
			# Multicast RESOURCE RELEASE message
			command = './send.py 9'
			if TEST == 1: 
				print command
			os.system(command)

		else:
			# Get all info of migration_candidates from a file
			fileHandel = open('migration_candidates_hotspot.txt', 'r')
			records = fileHandel.readlines()
			fileHandel.close()
			for record in records:
				record = record.strip('\n')
				array = record.split()
				key = array[0] + ':' + array[2] + ':' + array[3] + ':' + array[4]
				VM_CANDIDATES[array[1]] = key
				# 0 = vm_migrate, 1 = pm_migrate, 2 = placement, 3 = predicted t total, 4 = source			
			#sorted_prediction_array = sorted(VM_CANDIDATES.items(), key=lambda d:d[1])
			if '1' in VM_CANDIDATES:
				(vm_migrate[0], placement[0], predicted_t[0], source[0]) = VM_CANDIDATES['1'].split(':')
			else:
				vm_migrate[0] = state
				placement[0] = 'nova'
				predicted_t[0] = 0.82
				source[0] = 1
				core[0] = 8
				EWMA_pm_load[0] = 0.5
			if '2' in VM_CANDIDATES:						
				(vm_migrate[1], placement[1], predicted_t[1], source[1]) = VM_CANDIDATES['2'].split(':')
			else:
				vm_migrate[1] = state
				placement[1] = 'zone2'
				predicted_t[1] = 0.65
				source[1] = 2
				core[1] = 8
				EWMA_pm_load[1] = 0.5
			if '3' in VM_CANDIDATES:			
				(vm_migrate[2], placement[2], predicted_t[2], source[2]) = VM_CANDIDATES['3'].split(':')
			else:
				vm_migrate[2] = state
				placement[2] = 'zone3'
				predicted_t[2] = 1.23
				source[2] = 3
				core[2] = 4
				EWMA_pm_load[2] = 0.5
			if '4' in VM_CANDIDATES:
				(vm_migrate[3], placement[3], predicted_t[3], source[3]) = VM_CANDIDATES['4'].split(':')
			else:
				vm_migrate[3] = state
				placement[3] = 'zone4'
				predicted_t[3] = 1.23
				source[3] = 4
				core[3] = 4
				EWMA_pm_load[3] = 0.5

			#command = './multiarms.py ' + str(state_number) + ' ' + str(state) + ' ' + str(epsilon) + ' ' + str(accept_delay) + ' ' + str(predicted_t[0]) + ' ' + str(predicted_t[1]) + ' ' + str(predicted_t[2]) + ' ' + str(predicted_t[3])
	
			#comment out to select between moo, only t total and only load
			
			
			#scala use all but comment winner in ttotal and load
			# 
			command0 = './scalarized-multiarms.py ' + str(state_number) + ' ' + str(state) + ' ' + str(epsilon) + ' ' + str(weight_time) + ' ' + str(weight_load)
			if TEST == 1: 
				print command0
			os.system(command0)
			tcap = open(scala_node_select,'r')
			winner = tcap.read().strip()
			
			
			# only T total 
			#command1 = './multiarms.py ' + str(state_number) + ' ' + str(state) + ' ' + str(epsilon) + ' ' + str(1000*float(accept_delay)) + ' ' + str(1000*float(predicted_t[0])) + ' ' + str(1000*float(predicted_t[1])) + ' ' + str(1000*float(predicted_t[2])) + ' ' + str(1000*float(predicted_t[3]))

			# Scala and T total 
			command1 = './multiarms.py ' + str(state_number) + ' ' + str(state) + ' ' + str(epsilon) + ' ' + str(1000*float(accept_delay)) + ' ' + str(1000*float(predicted_t[0])) + ' ' + str(1000*float(predicted_t[1])) + ' ' + str(1000*float(predicted_t[2])) + ' ' + str(1000*float(predicted_t[3])) + ' ' + str(int(winner)-1)

			if TEST == 1: 
				print command1
			os.system(command1)

			#comment out these two line if run with scala
			#tcap = open(node_select,'r')
			#winner = tcap.read().strip()

			#end of only T total
						

			#only load
			EWMA_sum = map(sum, zip(EWMA_pm_load,load_accumulate_ad))

			#print "EWMA", EWMA_pm_load
			#print "load accumulate", load_accumulate_ad
			#only load
			#command2 = './multiarms-load.py ' + str(state_number) + ' ' + str(state) + ' ' + str(epsilon) + ' ' + str(vm_load) + ' ' + str(EWMA_sum[0]) + ' ' + str(EWMA_sum[1]) + ' ' + str(EWMA_sum[2]) + ' ' + str(EWMA_sum[3])

			# Scala and load
			command2 = './multiarms-load.py ' + str(state_number) + ' ' + str(state) + ' ' + str(epsilon) + ' ' + str(vm_load) + ' ' + str(EWMA_sum[0]) + ' ' + str(EWMA_sum[1]) + ' ' + str(EWMA_sum[2]) + ' ' + str(EWMA_sum[3]) + ' ' + str(int(winner)-1)

			if TEST == 1: 
				print command2
			os.system(command2)

			#comment out these two line if run with scala
			#tcap = open(load_node_select,'r')
			#winner = tcap.read().strip()

			load_accumulate_ad[int(winner)-1] += float(vm_load)/float(core[int(winner)-1])
			with open(load_accumulatenpy,'wb') as fp:
				pickle.dump(load_accumulate_ad,fp)
			#end of only load
			

			#print "Winner selected", sorted_prediction_array[0][0]
			#(vm_migrate, pm_migrate, placement, source) = sorted_prediction_array[0][0].split(':')
			
			print "Winner selected", winner
			#(vm_migrate, placement, predicted_t, source) = sorted_prediction_array[0][0].split(':')
			print "VM to place:", vm_migrate[int(winner)-1]
			print "PM for place:", winner
			print "Placement group for place:", placement[int(winner)-1]
			
			# Multicast WINNING BID ANNOUCEMENT message
			command = './send.py 7 ' + str(vm_migrate[int(winner)-1]) + ' ' + str(winner)  + ' ' + str(placement[int(winner)-1]) + ' ' + str(source[int(winner)-1])
			if TEST == 1: print command
			os.system(command)
			tcap.close()
				
# Function for applying backoff algorithm
def backoff():
	# Get configurations for the configure file
	config_dic=get_config()
	c = int(config_dic['COUNT'])
	b_c = random.uniform(0, 2**c - 1) * 0.5
	if b_c > 120: b_c = 120
	time.sleep(b_c)

global TEST, threshold_push, threshold_pull, strategy, VARIABLE_THRESHOLD, threshold_update_mean_time_min, limit

# Check for the arguments

if len(sys.argv) < 2:
	print "usage: " + sys.argv[0] + " MONITOR_INTERVAL"
	exit()

modify_config('HOTSPOT','0')
modify_config('COLDSPOT','0')
modify_config('COUNT','0')
modify_config('LOCK', '0:0')
modify_config('HOTSPOT_RECEIVE', 'no')
# Get configurations for the configure file
config_dic=get_config()
threshold_push = float(config_dic['THRESHOLD_PUSH'])
TEST = int(config_dic['TEST'])
interval = int(sys.argv[1])
HYPERVISOR = config_dic['HYPERVISOR']
file_path = 'request_vm.csv'
try:   
	while True:
		# Get configurations for the configure file
		config_dic=get_config()
		HOTSPOT = int(config_dic['HOTSPOT'])		
		lock = config_dic['LOCK']
		HOTSPOT_RECEIVE = config_dic['HOTSPOT_RECEIVE']
		#if cmp(HYPERVISOR.lower(), 'kvm') == 0:
		#	load=float(load_stat()['lavg_5'])
		#else: 
		#	print "Not available hypervisor, please specify kvm in setconfig.cfg"
		#	exit()
		#core=float(os.popen("nproc").read())
		#load_single=load/core 

		#timestamp = int(time.time())

		#if strategy == 1:
		#print 'Threshold for PUSH strategy', threshold_push
		# The case that HOTSPOT reached
		#if load_single>=threshold_push:
		#	threshold_push = float(config_dic['THRESHOLD_PUSH']) # Initial threshold

		#if cmp(HOTSPOT_RECEIVE.lower(), 'yes') == 0:

		request = raw_input("Make a request? yes/no \n")
		epis = input("Enter number of epis \n")
		mode = raw_input("Select a mode 1=fifo(default)/2=random/3=priority \n")
		weight = raw_input("Select a weight 1=time-0.75:load-0.25/2=time-0.50:load-0.50(default)/3=time-0.25:load-0.75 \n")
		if cmp(request.lower(), 'yes') == 0:
			eps = 0.5
			decay = 0.97
			if cmp(weight.lower(), '1') == 0:
				weight_time = 0.75
				weight_load = 0.25
			elif cmp(weight.lower(), '3') == 0:
				weight_time = 0.25
				weight_load = 0.75	
			else:
				weight_time = 0.5
				weight_load = 0.5
	
			with open(file_path) as csvf:
				data = csv.reader(csvf, delimiter=',')
				if cmp(mode.lower(), '2') == 0:
					header = []
					header.append(next(data))
					li = list(data)
					random.shuffle(li)
					data = header + li
					with open('result_dataset_random.csv','w') as writecsv:
						writer = csv.writer(writecsv)
						writer.writerows(data)
				if cmp(mode.lower(), '3') == 0:
					data = sorted(data, key=lambda row: row[5], reverse=False)
					with open('result_dataset_priority.csv','w') as writecsv:
						writer = csv.writer(writecsv)
						writer.writerows(data)
				#print(data)

			for i in range(epis):
				eps *= decay
				print('Round: ',i)
				print "New request!!!!!"
				timestamp = int(time.time())
				request_list = []
				#file_path = 'request_vm.csv'
				#with open(file_path) as csvf:
				#	data = csv.reader(csvf, delimiter=',')
				#	#print(data)
				with open(file_path) as csvf:
					data = csv.reader(csvf, delimiter=',')
					if cmp(mode.lower(), '2') == 0:
						header = []
						header.append(next(data))
						li = list(data)
						random.shuffle(li)
						data = header + li
						with open('result_dataset_random.csv','w') as writecsv:
							writer = csv.writer(writecsv)
							writer.writerows(data)
					if cmp(mode.lower(), '3') == 0:
						data = sorted(data, key=lambda row: row[5], reverse=False)
						with open('result_dataset_priority.csv','w') as writecsv:
							writer = csv.writer(writecsv)
							writer.writerows(data)
					for row in data:
						#print('new round')
						request_list.append(row)
						#print(len(request_list))
					for i in range (1,len(request_list)):
						if i <= 12:
							#vm_id = request_list[i][0]
							vm_id = i
							vm_vcpu = request_list[i][1]
							vm_disk = request_list[i][2]
							vm_load = request_list[i][3]
							vm_mem = request_list[i][4]
							accept_delay = request_list[i][5]
							print('id: ', vm_id, ' vcpu: ', vm_vcpu, ' disk: ', vm_disk, ' load: ', vm_load, ' mem: ', vm_mem, ' accept delay: ', accept_delay)
							send_command = './send.py 5 ' + str(vm_id) + ' ' + str(vm_vcpu) + ' ' + str(vm_disk) + ' ' + str(vm_load) + ' ' + str(vm_mem) + ' ' + str(accept_delay)
							print(send_command)
							if TEST == 1: print "Will send the HOTSPOT message"
							modify_config('HOTSPOT', str(timestamp))
							os.system(send_command)
							#modify_config('HOTSPOT_RECEIVE', 'no')
							# Start the timer for processing HOTSPOT REPLYS
							if (len(request_list)-1) <=12:
								state_request = len(request_list)-1
							else:
								state_request = 12
							decide_winner(state_request,i,eps,accept_delay,vm_load,weight_time,weight_load)
							#decide_winner(len(request_list)-1,i,eps,accept_delay)
						else:
							twait = open('result_accept_delay_queue.csv','a')
							twait.write(str(1000*float(request_list[i][5])))
							if i != (len(request_list)-1):
								twait.write(',')
							else:
								twait.write('\n')
							twait.close()

			'''
			if HOTSPOT ==0 or (timestamp-HOTSPOT)>60:
		
				if TEST == 1: print "Will send the HOTSPOT message"
				modify_config('HOTSPOT', str(timestamp))
				os.system('./send.py 5')
				modify_config('HOTSPOT_RECEIVE', 'no')
				# Start the timer for processing HOTSPOT REPLYS
				thread.start_new_thread(decide_winner,(),)
			else: 
				if TEST == 1: print "already send the HOTSPOT message, waiting for the replys"
				modify_config('HOTSPOT_RECEIVE', 'no')		
			'''
		else: 
			print "Waiting for Hotspot request!!!!!"
		
		time.sleep(interval)
		backoff()   
except KeyboardInterrupt:  
	print "User Press Ctrl+C,Exit" 
except EOFError:  
	print "User Press Ctrl+D,Exit"
'''

config_dic=get_config()
TEST = int(config_dic['TEST'])
decide_winner()
'''
