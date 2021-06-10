#!/usr/bin/python2

# Keep listening to the socket for the communication protocal
import socket, struct, LMA_measurement, pickle, os, thread, sys, datetime, time
from tools import host_existed_IP, host_existed_ID, latest_ID, find_ID_by_IP, get_config, vm_existed, modify_config, vm_local
from sys_tools import load_stat, memory_stat, net_stat

global lock, TEST

# Function to check whether the PM are ready to deal with messages from other PMs
def membership(address):
	hosts = []

	# The case when the hosts list does not exist
	if not os.path.isfile('Hosts.txt'):
		if TEST == 1: print "new.. say hello first"
		return (False, hosts)

	fileHandel = open('Hosts.txt','r')
	hosts = fileHandel.readlines()
	fileHandel.close()

	# The case that the 'localhost' is not in the list, new to the network, pass
	if not host_existed_IP(hosts, 'localhost'):
		if TEST == 1: print "new.. say hello first"
		return (False, hosts)

	#The case that the source host is not in the list, pass
	if not host_existed_IP(hosts, address[0]):
		if TEST == 1: print 'unknown host -> pass'
		return (False, hosts)

	return (True, hosts)

# Function to automatically release resource after replying to HOTSPOT MESSAGE for PUSH strategy
def auto_release(boss):
	time.sleep(60)
	global lock
	# Get configurations for the configure file
	config_dic=get_config()

	lock = config_dic['LOCK']
	if cmp(lock,boss) == 0:
		if TEST == 1: print "Release resource automatically"
		try:
			modify_config('LOCK', '0:0')
		except TypeError:
			print 'here'

# Function to response to messages
def deal_with_packet(buf, address):
		global lock, TEST
		if not len(buf):                                
			return 0
		if TEST == 1: 
			print "\n***********************************"
			print "Received from", address

		buffer=pickle.loads(buf)

		# Check for the format of the message
		if not isinstance(buffer,LMA_measurement.LVA_unit):
			print "WRONG UNIT FORMAT!"
			return 0

		if TEST == 1: 
			print "Source_node", buffer.Source_node
			print "Destination_node", buffer.Destination_node
			print "Message_type", buffer.Message_type
			print "Content", buffer.Content

		#nomal node mode
		if int(sys.argv[1])==0:
			if buffer.Source_node != 0:
				c = datetime.datetime.now()
                		current = c.strftime('%Y-%m-%d %H:%M:%S:%f')

				log_file = open('host_log.txt', 'a')
				log_line = '%s: Receive %s(%s) from %s(%s)\n' % (current, buffer.Message_type, buffer.Content, buffer.Source_node, address)
				log_file.write(log_line)
				log_file.close()

			####################################
			#####																#####
			#####		Receive HELLO message -- 1		#####
			#####																#####
			##### 		 --> Reply HELLO REPLY  -- 2		#####
			#####																##### 
			####################################
			if buffer.Message_type==1:
				# The case when the hosts list does not exist
				if not os.path.isfile('Hosts.txt'):
					if TEST == 1: print "new.. say hello first"
					return 0

				fileHandel = open('Hosts.txt','r')
				hosts = fileHandel.readlines()
				fileHandel.close()

				# The case that the 'localhost' is not in the list, new to the network, pass
				if not host_existed_IP(hosts, 'localhost'):
					if TEST == 1: print "new.. say hello first"
					return 0

				reply_unit=LMA_measurement.LVA_unit()
				reply_unit.Message_type=2
				reply_unit.Content="Reply"

				# Specify the Source_node as own ID
				reply_unit.Source_node=find_ID_by_IP(hosts, 'localhost')

				# The case that the greeting host is already in the list, pass
				if host_existed_IP(hosts, address[0]):
					if TEST == 1: print 'IP exists'
					return 0

				# The case that the message is from the self host, pass
				if buffer.Source_node == find_ID_by_IP(hosts, 'localhost'):
					if TEST == 1: print "message from self, pass"
					return 0

				# The case that the greeting host is not in the list, prepare to update the list
				if TEST == 1: print 'new IP -> update Hosts list'
				
				# The case that the greeing host is new to the network, specify its ID
				if buffer.Source_node == 0:
					des_node = long(latest_ID(hosts)+1)
					if TEST == 1: print "new host for the network:", des_node, address[0]
					
				# The case that the greeting host already has an ID, update the list
				else:
					des_node = buffer.Source_node
					if TEST == 1: print "new host for this host :", des_node, address[0]
					
				fileHandel = open('Hosts.txt','a')
				item = str(des_node) + ' ' + address[0] + '\n'
				if TEST ==1: print "Content to update the list:", item
				fileHandel.write(item)
				fileHandel.close()
				reply_unit.Destination_node=des_node

				# Package the message and send it
				reply=pickle.dumps(reply_unit)
				s.sendto(reply, address)
				print "send HELLO reply"  
				return 0

			#######################################
			#####																		#####
			#####		Receive HOTSPOT message  -- 5		#####
			#####																		#####
			#####		--> Reply HOTSPOT REPLY  -- 6 			#####
			#####																		##### 
			####################################### 
			if buffer.Message_type == 5:
				# Check whether the PMs are already members of the network
				(check, hosts) = membership(address)
			        config_dic=get_config()
				if not check: return 0
				if config_dic['HOTSPOT_RECEIVE'] == 'yes': return 0
				if TEST == 1: print "save buffer into a file"
				fileHandel1 = open('buffer_hotspot_message_source.txt','w')
				fileHandel2 = open('buffer_hotspot_message_VM.txt','w')
				print buffer.Source_node, buffer.VM_info
				pickle.dump(buffer.Source_node, fileHandel1)
				for vm in buffer.VM_info:
					pickle.dump(vm, fileHandel2)
				fileHandel1.close()
				fileHandel2.close()
				modify_config('HOTSPOT_RECEIVE', 'yes')
				'''
			        config_dic=get_config()
				reply_unit = LMA_measurement.LVA_unit()
				reply_unit.Message_type = 6
				reply_unit.Content = "HOTSPOT Reply"

				reply_unit.Source_node = find_ID_by_IP(hosts, 'localhost')
				reply_unit.Destination_node=buffer.Source_node

				# Generate the PM infomation
				val = os.popen("cat /proc/cpuinfo | grep \"processor\" | wc -l")
				PM_cores = int(val.read())
				com = "df %s | sed 1d | awk '{print $4}'" %config_dic['DISK']
				val2 = os.popen(com)
				disk_free = int(val2.read())
				reply_unit.PM_info.ID = find_ID_by_IP(hosts, 'localhost')
				reply_unit.PM_info.CPU_max= PM_cores
				fileHandel = open('pm_info.txt', 'r')
				data = fileHandel.readline().split()
				fileHandel.close()
				reply_unit.PM_info.CPU_current = float(data[0])
				reply_unit.PM_info.CPU_record = float(data[1]) 
				reply_unit.PM_info.MEM_max = memory_stat()['MemTotal']
				reply_unit.PM_info.MEM_used = memory_stat()['MemUsed']
				reply_unit.PM_info.placement_group = config_dic['PLACEMENT_GROUP']
				command = './mpredicttotal.py'
				#os.system(command)

			        # Get configurations for the configure file
			        #config_dic=get_config()
				f = open("t_total.txt", "r")
      				lock = config_dic['LOCK']

				# The case when resource is locked
				if cmp(lock, '0:0') !=  0:
					if TEST == 1: print "Resource locked -> pass"
					# Package the message and send it
					reply=pickle.dumps(reply_unit)
					s.sendto(reply, address)
					return 1

				if TEST == 1: print "recieve HOTSPOT MESSAGE -> resource locked by", buffer.Source_node
				lock = '%s:%s' % (int(time.time()), buffer.Source_node)
				modify_config('LOCK', lock)

				# Generate the VM infomations
				VMs = buffer.VM_info
				mem_free= memory_stat()['MemTotal'] - memory_stat()['MemUsed']
				print "MemFree", mem_free, "PM_cores", PM_cores, "DiskFree", disk_free
				EWMA_pm_load = 0.2 * float(data[1]) + 0.8 * float(data[0])
				for vm in VMs:					
					if TEST == 1: print vm.ID, vm.MEM, vm.Virtual_cores_num, vm.disk, vm.IP_host, vm.IP_rs, vm.IP_ue
					if vm.MEM > mem_free:
						print "Mem too big -> sorry"
					#	continue
					#disk_req = int(vm.disk) * 1048576			
					#if disk_req > disk_free:
					#	print "Size too big -> sorry"
					#	continue
					if len(vm.IP_rs) == 0:
						print "No application running -> sorry"
					#	continue
					EWMA_vm_load = 0.2 * vm.CPU_record + 0.8 * vm.CPU_current
					# Get configurations for the configure file
					config_dic=get_config()
					if (EWMA_vm_load + EWMA_pm_load)/PM_cores > config_dic['THRESHOLD_PUSH']: 
						print (EWMA_vm_load + EWMA_pm_load)/PM_cores, "Load -> sorry"
					else:
						for predict in f:
							a = predict.split()		
							for i in range(len(vm.IP_rs)):
								if a[0] == vm.IP_rs[i] and a[1] == vm.IP_ue[i]:
									vm.predict = float(a[2])
									print "Predict: %s %s: Add one vm into the candidates list" %(vm.IP_rs[i],vm.IP_ue[i])						
									reply_unit.VM_info.append(vm)
								else:
									print "No prediction match this VM"

				# Package the message and send it
				reply=pickle.dumps(reply_unit)
				s.sendto(reply, address)

				# WINNING BID ANNOUNCEMNET does not arrive, release resource automatically
				thread.start_new_thread(auto_release,(lock, ),)
				'''
				return 1

			#######################################################
			#####																												#####
			#####		Receive WINNING BID ANNOUNCEMENT message -- 7		#####
			#####																												#####
			#####		 --> Reply WINNING BID ACKNOWLEDGMENT  -- 8				#####
			#####																												##### 
			#######################################################
			if buffer.Message_type==7:
				# Get configurations for the configure file
			        config_dic=get_config()

			        lock = int(config_dic['LOCK'].split(':')[1])
				if TEST == 1: 
					print "recieve WINNING BID ANNOUNCEMENT", lock
					print "source:", buffer.Source_node

				# Not participant
				if lock == 0:
					if TEST == 1: print "not participant" 
					return 0

				# Not my boss
				if lock != buffer.Source_node: 
					if TEST == 1: print "not my boss"
					return 0

				# Check whether the PMs are already members of the network
				(check, hosts) = membership(address)
				if not check: return 0

				if TEST == 1: print buffer.Migration_issuer

				# The case that I am not the winner -> resource release
				if buffer.Migration_issuer != find_ID_by_IP(hosts, 'localhost'):
					if TEST == 1: print "Resource release"
					modify_config('LOCK', '0:0')
				else: 
					if TEST == 1: print "I am the winner!!!"
					reply_unit=LMA_measurement.LVA_unit()
					reply_unit.Message_type=8
					reply_unit.Content="WINNING BID ACKNOWLEDGMENT"
					reply_unit.Destination_node=buffer.Source_node
					reply_unit.Source_node=find_ID_by_IP(hosts, 'localhost')
					reply_unit.Migration_id=buffer.Migration_id
					reply_unit.Migration_issuer=buffer.Migration_issuer
					reply_unit.Placement=buffer.Placement

					# Package the message and send it
					reply=pickle.dumps(reply_unit)
					s.sendto(reply, address)
				return 1

			#############################################
			#####																						#####
			#####		Receive RESOURCE RELEASE message -- 9		#####
			#####																						#####
			#############################################
			if buffer.Message_type==9:
				# Check whether the PMs are already members of the network
				(check, hosts) = membership(address)
				if not check: return 0

				if TEST == 1: print "receive RESOURCE RELEASE message"

			        # Get configurations for the configure file
			        config_dic=get_config()

			        lock = int(config_dic['LOCK'].split(':')[1])
				if lock == 0: 
					if TEST == 1: print "resource not locked"
				elif lock != buffer.Source_node: 
					if TEST == 1: print "not my boss"
				else: 
					if TEST == 1: print "release resouce"
					modify_config('LOCK', '0:0')
				return 1

			########################################################
			#####																													#####
			#####		Receive  MIGRATION ACKNOWLEDGMENT  message -- 4		#####
			#####																													#####
			########################################################
			if buffer.Message_type==4:
				# Check whether the PMs are already members of the network
				(check, hosts) = membership(address)
				if not check: return 0

				# Get configurations for the configure file
				config_dic=get_config()
				COLDSPOT =int(config_dic['COLDSPOT'])

				# The case that it's the coldspot. Reset COLDSPOT
				if COLDSPOT != 0:
					modify_config('COUNT', '0')
					modify_config('COLDSPOT','0')
					time.sleep(30)
					modify_config('LOCK', '0:0')
					return 1

				# In PUSH strategy, deal with the locked resource
				else:
				        # Get configurations for the configure file
				        config_dic=get_config()

				        lock = int(config_dic['LOCK'].split(':')[1])
					if lock == 0: 
						if TEST == 1: print "I am not locked"
						return 0
					if lock != buffer.Source_node:
						if TEST == 1: print "I am not locked because of it"
						return 0
					else: 
						if TEST == 1: print "Migration finished -> Resource release"
						time.sleep(30)
						modify_config('LOCK', '0:0')
						return 1
			
			###################################################
			#####																										#####
			#####			Receive  MEASUREMENT REQUEST message -- 14		#####
			#####																										#####
			#####		--> Reply MEASUREMENT REPLY -- 15								#####
			#####																										#####
			###################################################
			if buffer.Message_type==14:	
				# The case when the hosts list does not exist
				if not os.path.isfile('Hosts.txt'):
					if TEST == 1: print "new.. say hello first"
					return 0

				fileHandel = open('Hosts.txt','r')
				hosts = fileHandel.readlines()
				fileHandel.close()

				# The case that the 'localhost' is not in the list, new to the network, pass
				if not host_existed_IP(hosts, 'localhost'):
					if TEST == 1: print "new.. say hello first"
					return 0

				if TEST == 1: print "recieve Measurement request, prepare PM_info as reply"
				reply_unit = LMA_measurement.LVA_unit()
				reply_unit.Message_type = 15
				reply_unit.Content = "MEASUREMENT Reply"

				reply_unit.Source_node = find_ID_by_IP(hosts, 'localhost')
				reply_unit.Destination_node=buffer.Source_node

				# Generate the PM infomation
				val = os.popen("cat /proc/cpuinfo | grep \"processor\" | wc -l")
				PM_cores = int(val.read())
				reply_unit.PM_info.ID = find_ID_by_IP(hosts, 'localhost')
				reply_unit.PM_info.CPU_max= PM_cores
				fileHandel = open('pm_info.txt', 'r')
				data = fileHandel.readline().split()
				fileHandel.close()
				reply_unit.PM_info.CPU_current = float(data[0])
				reply_unit.PM_info.CPU_record = float(data[1]) 
				reply_unit.PM_info.MEM_max = memory_stat()['MemTotal']
				reply_unit.PM_info.MEM_used = memory_stat()['MemUsed']
				reply_unit.PM_info.Traffic_Bytes = int(net_stat()['ReceiveBytes']) + int(net_stat()['TransmitBytes']) 
				reply_unit.PM_info.Traffic_packets = int(net_stat()['ReceivePackets']) + int(net_stat()['TransmitPackets']) 

				# Package the message and send it
				reply=pickle.dumps(reply_unit)
				s.sendto(reply, address)

		#server mode
		if int(sys.argv[1])==1:

			##########################################
			#####																				#####
			#####			Receive  MIGRATION message -- 3		#####
			#####																				#####
			##########################################
			if buffer.Message_type==3:
				# Get configurations for the configure file
				config_dic=get_config()
				migration_attemps = int(config_dic['MIGRATION_ATTEMPS'])
				modify_config('MIGRATION_ATTEMPS', str(migration_attemps + 1))
				fileHandel = open('log.txt','a')
				current = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')
				line = "%s %s%s: %s\n" % (current, buffer.Source_node, address, buffer.Content)
				fileHandel.write(line)
				fileHandel.close()

			########################################################
			#####																													#####
			#####		Receive  MIGRATION ACKNOWLEDGMENT  message -- 4		#####
			#####																													#####
			########################################################
			if buffer.Message_type==4:
				# Get configurations for the configure file
				config_dic=get_config()
				migration_attemps = int(config_dic['MIGRATIONS'])
				modify_config('MIGRATIONS', str(migration_attemps + 1))
				c = datetime.datetime.now()
				fileHandel = open('log.txt','a')
				current = c.strftime('%Y-%m-%d %H:%M:%S:%f')
				line = "%s %s%s: %s\n" % (current, buffer.Source_node, address, buffer.Content)
				fileHandel.write(line)
				fileHandel.close()

			##########################################
			#####                                                         						#####
			#####           Receive HOTSPOT message  -- 5           #####
			#####                                                                               ##### 
			##########################################
			'''
			if buffer.Message_type == 5:
				# Get configurations for the configure file
				config_dic=get_config()
				help_request = int(config_dic['HELP_REQUEST'])
				modify_config('HELP_REQUEST', str(help_request + 1))
				c = datetime.datetime.now()
				fileHandel = open('request.txt','a')
				current = c.strftime('%Y-%m-%d %H:%M:%S:%f')
				line = "%s %s: PM%s sends a HOTSPOT message.\n" % (current, address, buffer.Source_node)
				fileHandel.write(line)
				fileHandel.close()
			'''			
# Check for the arguments
if len(sys.argv) < 2:
	print "usage: " + sys.argv[0] + " node_mode[1|0]"
	print "Node mode: 1 for server mode; 0 for normal node mode."
	exit()

modify_config('LOCK','0:0')
modify_config('COLD_LOCK', '0')
# Get configurations for the configure file
config_dic=get_config()

address = ('', int(config_dic['MULTICAST_PORT']))
multicast_group = config_dic['MULTICAST_ADDR']

TEST =int(config_dic['TEST'])
HYPERVISOR = config_dic['HYPERVISOR']

# Create the socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
# Bind to the server address
s.bind(address)

# Tell the operating system to add the socket to the multicast group on all interfaces.
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

if int(sys.argv[1])==0:
	print "running as normal node mode"
else:
	print "Running as server mode" 

try:
	# Receive/respond loop
	while True:
		thread.start_new_thread(deal_with_packet, (s.recvfrom(2048) ), )

except KeyboardInterrupt:
	print "User Press Ctrl+C,Exit"
except EOFError:
	print "User Press Ctrl+D,Exit"

s.close() 
exit()
