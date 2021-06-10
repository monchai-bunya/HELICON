#!/usr/bin/python2

# Send corresponding messages for push and pull strategies
import socket, struct, sys, LMA_measurement, pickle, os, datetime, time
from tools import host_existed_IP, host_existed_ID, latest_ID, find_ID_by_IP, find_IP_by_ID, get_config, modify_config, vm_existed, update_candidates, find_vm_name_by_id
from sys_tools import load_stat, memory_stat

# Function to check whether the host is a member of the network
def membership():
	# The case when the hosts list does not exist
	if not os.path.isfile('Hosts.txt'):
		print "new in the network, say hello first"
		exit()

	if TEST == 1: print "Hosts list obtained"
	fileHandel = open('Hosts.txt','r')
	hosts = fileHandel.readlines()
	fileHandel.close()

	# The case that 'localhost' is not in the hosts list
	if not host_existed_IP(hosts, 'localhost'):
		print "new in the network, say hello first"
		exit()

	return hosts

# Function to check when to stop receiving new messages
def exit_check():
	print Reply_num, Exit_num
	if Reply_num >= Exit_num:
		print 'Exit.'
		s.close()
		exit()

# Function for applying timeout algorithm
def exit_timeout():
	print "Time out."
	s.close()
	exit()

# Check for the arguments
if len(sys.argv) < 2:
	print "usage: " + sys.argv[0] + " Message_type [Options]"
	exit()

# Get configurations for the configure file
config_dic=get_config()
multicast_group = (config_dic['MULTICAST_ADDR'], int(config_dic['MULTICAST_PORT']))

global TEST, HOTSPOT, COLDSPOT, VM_CANDIDATES, VM_candidates_info, PM_candidates_info,Exit_num, Reply_num, t
TEST = int(config_dic['TEST'])
HOTSPOT = int(config_dic['HOTSPOT'])
COLDSPOT = int(config_dic['COLDSPOT'])
HYPERVISOR = config_dic['HYPERVISOR']
VM_CANDIDATES={}
VM_candidates_info={}
PM_candidates_info={}

# Create the datagram socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Set a timeout so the socket does not block indefinitely
s.settimeout(30)

# Set the time-to-live for messages to 1
ttl = struct.pack('b', 1)
s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

c = datetime.datetime.now()
current = c.strftime('%Y-%m-%d %H:%M:%S:%f')

log_file = open('host_log.txt', 'a')
log_line = '%s: Send %s(%s)\n' % (current, sys.argv[1], LMA_measurement.Message_types[sys.argv[1]])
log_file.write(log_line)
log_file.close()

####################################
#####															#####
#####		Sending HELLO message -- 1		#####
#####															##### 
####################################
if int(sys.argv[1])==1:
	message_unit=LMA_measurement.LVA_unit()
	message_unit.Message_type=1
	message_unit.Content="Hello"
	if not os.path.isfile('Hosts.txt'):
		if TEST == 1: print "The first time to say hello: SEND HELLO(1)..."
	else:
		fileHandel = open('Hosts.txt','r')
		hosts = fileHandel.readlines()
		fileHandel.close()
		if host_existed_IP(hosts, 'localhost'):
			if TEST == 1: print "Say hello again: SEND HELLO(1)..."
			message_unit.Source_node = find_ID_by_IP(hosts, 'localhost')
		else:
			if TEST == 1: print "Hosts list obtained, regard as the first time to say hello: SEND HELLO(1)"

	# Package the message and send it
	message=pickle.dumps(message_unit)
	s.sendto(message, multicast_group)
	s.settimeout(5)

######################################
#####																#####
#####		Sending HOTSPOT message -- 5		#####
#####																##### 
######################################
elif int(sys.argv[1])==5:
	# Check whether the PM is already a member of the network
	hosts = membership()

	if TEST == 1: print 'preparing the HOTSPOT message...'
	message_unit = LMA_measurement.LVA_unit()

	# Get configurations for the configure file
	config_dic=get_config()
	COLD_LOCK = config_dic['COLD_LOCK'].split(':')
     
	# prepare for the VM_info
	command = "./vm_list.py %s | sed -e 1d" % HYPERVISOR
	val = os.popen(command)
	results = val.readlines()
	#print results
	for result in results:
		array = result.split()

		'''
		if TEST == 1: print "vm_id:", array[0]
		if int(array[0]) == 0:
			if TEST == 1: print array[8], "not to be considered" 
		elif cmp(array[2], 'paused') == 0 or cmp(array[2], 'shutdown') == 0:
			if TEST == 1: print array[8], "not running, ignored"		
		else:
		''' # if uncomment 1 tab for next
		if cmp(array[6],'NaN') == 0:
			if TEST == 1: print array[8], "has not response"
		else:
			#vm_locked = 0
			#for COLD_LOCK_id in COLD_LOCK:
			#	if int(COLD_LOCK_id) == int(array[0]):
			#		vm_locked = 1
			#		break
			#if vm_locked == 0:
				#prepare VM_info
			VM_info_item = LMA_measurement.VM_info()
			VM_info_item.ID = array[0]
			#VM_info_item.ID = int(array[0])
			VM_info_item.Virtual_cores_num = array[3]
			#VM_info_item.Virtual_cores_num = int(array[3])
			VM_info_item.disk = array[2]
			#VM_info_item.disk = float(array[2])
			VM_info_item.CPU_current = float(array[6])
			VM_info_item.CPU_record= float(array[7])
			VM_info_item.MEM = array[4]
			#VM_info_item.MEM = int(array[4])
			VM_info_item.Page_dirty_rate = float(array[5])
			
			if array[9] != 'NaN':
				for i in range(int(array[9])):
					j = 10 + i*3
					k = 11 + i*3
					l = 12 + i*3
					VM_info_item.IP_host.append(array[j])
					VM_info_item.IP_rs.append(array[k])
					VM_info_item.IP_ue.append(array[l])
				
			message_unit.VM_info.append(VM_info_item)

					#prepare RP_info
				#else:
				#	if TEST == 1: print array[8], "is locked." 
				#	continue
  
	message_unit.Source_node = find_ID_by_IP(hosts, 'localhost')
	message_unit.Message_type = 5
	message_unit.Content = "Hot spot"

	# Package the message and send it
	message = pickle.dumps(message_unit)
	s.sendto(message, multicast_group)

	print message_unit.VM_info
	#print message
	if os.path.isfile('migration_candidates_hotspot.txt'): os.remove('migration_candidates_hotspot.txt')
	if os.path.isfile('VM_candidates_hotspot.txt'): os.remove('VM_candidates_hotspot.txt')
	if os.path.isfile('PM_candidates_hotspot.txt'): os.remove('PM_candidates_hotspot.txt')
	if TEST == 1: print "size of packge:", len(message)

	Exit_num = len(hosts) - 1

######################################################
#####																									#####
#####		Sending WINNING BID ANNOUNCEMENT message -- 7		#####
#####																									##### 
######################################################
elif int(sys.argv[1])==7:
	if len(sys.argv) < 4: 
		print "Please tell the winner.\nUsage:", sys.argv[0], "7 winner_bid pm_to_migrate"
		exit() 

	# Check whether the PM is already a member of the network
	hosts = membership()

	message_unit=LMA_measurement.LVA_unit()
	message_unit.Message_type=7
	message_unit.Content="WINNING BID ANNOUNCEMENT"
	message_unit.Source_node=find_ID_by_IP(hosts, 'localhost')
	#message_unit.Migration_id=long(sys.argv[2])
	message_unit.Migration_id=sys.argv[2]
	message_unit.Migration_issuer=long(sys.argv[3])
	message_unit.Placement=sys.argv[4]
	if TEST == 1: print "SEND WINNING BID ANNOUNCEMENT: winner", sys.argv[2]

	# Package the message and send it
	message=pickle.dumps(message_unit)
	s.sendto(message, multicast_group)
	Exit_num = 1

#############################################
#####																				#####
#####		Sending RESOURCE RELEASE message -- 9		#####
#####																				##### 
#############################################
elif int(sys.argv[1])==9:
	# Check whether the PM is already a member of the network
	hosts = membership()

	message_unit=LMA_measurement.LVA_unit()
	message_unit.Message_type=9
	message_unit.Content="RESOURCE RELEASE"
	message_unit.Source_node=find_ID_by_IP(hosts, 'localhost')

	# Package the message and send it
	message=pickle.dumps(message_unit)
	s.sendto(message, multicast_group)
	modify_config('HOTSPOT', '0')
	# Get configurations for the configure file
	config_dic=get_config()
	c = int(config_dic['COUNT'])
	modify_config('COUNT', str(c+1))
	exit()

##################################################
#####																							#####
#####		Sending MEASUREMENT REQUEST message -- 14		#####
#####																							##### 
##################################################
elif int(sys.argv[1])==14:
	message_unit=LMA_measurement.LVA_unit()
	message_unit.Message_type=14
	message_unit.Content="MEASUREMENT REQUEST"

	# Package the message and send it
	message=pickle.dumps(message_unit)
	s.sendto(message, multicast_group)

	if os.path.isfile('PM_infos.txt'): os.remove('PM_infos.txt')
	s.settimeout(1)

#######################################
#####																	#####
#####		Sending MIGRATION message -- 3		#####
#####																	##### 
#######################################
elif int(sys.argv[1])==3:
	if len(sys.argv) < 5: 
		print "Usage:", sys.argv[0], "3 Migration_id Destination_node Placement_group"
		exit()

	# Check whether the PM is already a member of the network
	hosts = membership()

	message_unit=LMA_measurement.LVA_unit()
	message_unit.Message_type=3
	message_unit.Content="MIGRATION:Migrate %s to %s(%s) at %s" % (sys.argv[2], sys.argv[3], find_IP_by_ID(hosts, int(sys.argv[3])), sys.argv[4])
	#message_unit.Content="MIGRATION:Migrate %s to %s(%s)" % (find_vm_name_by_id(sys.argv[2]), sys.argv[3], find_IP_by_ID(hosts, int(sys.argv[3])))
	message_unit.Source_node=find_ID_by_IP(hosts, 'localhost')
	message_unit.Migration_issuer=long(sys.argv[3])
	message_unit.Migration_id=sys.argv[2]
	message_unit.Placement=sys.argv[4]
	#message_unit.Migration_id=long(sys.argv[2])

	server_address = (config_dic['SERVER_IP'], int(config_dic['MULTICAST_PORT']))
	# Package the message and send it
	message=pickle.dumps(message_unit)
	s.sendto(message, server_address)
	s.close()
	exit()

else:
	if TEST == 1: 
		print "Not available"
		exit()

Reply_num = 0
try:
	# Get configurations for the configure file
	config_dic=get_config()

	HOTSPOT = int(config_dic['HOTSPOT'])
	COLDSPOT = int(config_dic['COLDSPOT'])

	# Receive/respond loop
	while True:
		(buf, address) = s.recvfrom(2048)  

		if not len(buf):
			continue
		if TEST == 1: 
			print "\n***********************************"
			print "Received from", address

		buffer=pickle.loads(buf)

		# Check for the format of the message
		if not isinstance(buffer,LMA_measurement.LVA_unit):
			print "WRONG UNIT FORMAT!"
			continue

		if TEST == 1: 
			print "Source_node", buffer.Source_node
			print "Destination_node", buffer.Destination_node
			print "Message_type", buffer.Message_type
			print "Content", buffer.Content

		Reply_num += 1

		c = datetime.datetime.now()
                current = c.strftime('%Y-%m-%d %H:%M:%S:%f')

		log_file = open('host_log.txt', 'a')
		log_line = '%s: Receive %s(%s) from %s(%s)\n' % (current, buffer.Message_type, buffer.Content, buffer.Source_node, address)
		log_file.write(log_line)
		log_file.close()
		########################################
		#####																	#####
		#####		Receive HELLO RELPY message -- 2		#####
		#####																	#####
		########################################
		if buffer.Message_type == 2:
			
			if buffer.Source_node == 0: continue 

			# The case when the hosts list exists
			if os.path.isfile('Hosts.txt'):
				fileHandel = open('Hosts.txt','r')
				hosts = fileHandel.readlines()
				fileHandel.close()

				# The case that 'localhost' is in the hosts list
				if host_existed_IP(hosts, 'localhost'): 
					pass
				# 'localhost' not in the hosts list, insert a record
				else: 
					fileHandel = open('Hosts.txt','a')
					item = str(buffer.Destination_node) + ' localhost\n'
					print item
					fileHandel.write(item)
					fileHandel.close()

				# The source host of the recieved package is already in the hosts list
				if host_existed_IP(hosts, address[0]):
					print 'IP exists'
					pass
				# Add a new host 
				else:
					print 'IP does not exist'
					fileHandel = open('Hosts.txt','a')
					item = str(buffer.Source_node) + ' ' + address[0] + '\n'
					print item
					fileHandel.write(item)
					fileHandel.close()
			# Create a new file and add new records
			else:
				fileHandel = open('Hosts.txt','w')
				item = str(buffer.Source_node) + ' ' + address[0] + '\n'
				print item
				fileHandel.write(item)
				item = str(buffer.Destination_node) + ' localhost\n'
				print item
				fileHandel.write(item)
				fileHandel.close()

		###########################################
		#####																			#####
		#####		Receive HOTSPOT REPLY  message -- 6		#####
		#####																			#####
		###########################################
		if buffer.Message_type==6:

			config_dic=get_config()
			if HOTSPOT == 0: pass
			if cmp(config_dic['OSM'].lower(), 'yes') != 0: exit()
			else:
				if TEST == 1: print "save info for the PM into a file"
				fileHandel = open('PM_candidates_hotspot.txt','a')
				pickle.dump(buffer.PM_info, fileHandel)
				fileHandel.close()

				if len(buffer.VM_info) == 0: 
					if TEST == 1: print "no candidates"
				else:
					for vm in buffer.VM_info:
						if TEST == 1: print vm.ID
						if vm_existed(vm.ID): 
							if TEST == 1: print "update info for the vm_candidate"
							update_candidates(vm.ID, buffer.Source_node)
						else:
							if TEST == 1: print "a candidate: vm", vm.ID  
							if TEST == 1: print "save info for the VM into a file"
							fileHandel = open('VM_candidates_hotspot.txt','a')
							pickle.dump(vm, fileHandel)
							fileHandel.close()

							if TEST == 1: print "insert a record info for the vm_candidate"
							fileHandel = open('migration_candidates_hotspot.txt','a')
							#record = str(vm.ID) + ' ' + str(buffer.Source_node) + ' ' + str(vm.predict) + '\n'
							#record = str(vm.IP_host[0]) + ' ' + str(buffer.Source_node) + ' ' + str(buffer.PM_info.placement_group) + ' ' + str(vm.predict) + '\n'
							record = str(vm.ID) + ' ' + str(buffer.Source_node) + ' ' + str(buffer.PM_info.placement_group) + ' ' + str(vm.predict) + '\n'
							fileHandel.write(record)
							fileHandel.close()

		########################################################
		#####																										#####
		#####		Receive  WINNING BID ACKNOWLEDGMENT message -- 8		#####
		#####																										#####
		########################################################
		if buffer.Message_type==8:

			fileHandel = open('Hosts.txt','r')
			hosts = fileHandel.readlines()
			fileHandel.close()
 
			if not buffer.Destination_node==find_ID_by_IP(hosts, 'localhost'):
				if TEST == 1: print "not my business, wrong message"
			else:
				# Get configurations for the configure file
				config_dic=get_config()
				COLD_LOCK = config_dic['COLD_LOCK'].split(':')
				if cmp(config_dic['OSM'].lower(), 'yes') != 0: exit()
				result=1
				'''
				for COLD_LOCK_id in COLD_LOCK:
					if int(COLD_LOCK_id) == buffer.Migration_id:
						result =0
				'''
				if result==0:
					# Get configurations for the configure file
					config_dic=get_config()
					c = int(config_dic['COUNT'])
					modify_config('COUNT', str(c+1))
					modify_config('HOTSPOT', '0')
					s.close()
					exit()
				else:
					modify_config('COUNT', '0')
					# Get configurations for the configure file
					config_dic=get_config()
					COLD_LOCK = config_dic['COLD_LOCK'].split(':')

					# Lock the VM for migration
					COLD_LOCK.append(str(buffer.Migration_id))
					COLD_LOCK_item = ':'.join(COLD_LOCK)
					modify_config('COLD_LOCK', COLD_LOCK_item)

					# Send MIGRATION message to server for generating migration attemps
					command = './send.py 3 ' + str(buffer.Migration_id) + ' ' + str(buffer.Migration_issuer) + ' ' + str(buffer.Placement)
					if TEST == 1: print command
					os.system(command)

					if TEST == 1: print "preparing for the migration"
					if TEST == 1: print "will migrate VM", buffer.Migration_id, "to PM",  buffer.Migration_issuer, "at",  buffer.Placement, "..."
					reply_unit=LMA_measurement.LVA_unit()
					reply_unit.Message_type=4
					migrate_record = (buffer.Migration_id, buffer.Migration_issuer, find_IP_by_ID(hosts, buffer.Migration_issuer), buffer.Placement)
					#migrate_record = (find_vm_name_by_id(str(buffer.Migration_id)), buffer.Migration_issuer, find_IP_by_ID(hosts, buffer.Migration_issuer))
					reply_unit.Content="MIGRATION ACKNOWLEDGMENT:Migrate %s to %s(%s) at %s" % migrate_record
					reply_unit.Destination_node=buffer.Source_node
					reply_unit.Source_node=find_ID_by_IP(hosts, 'localhost')
					reply_unit.Migration_issuer=buffer.Source_node
					command="./live-migrate.py %s id:%s %s %s" % (HYPERVISOR, str(buffer.Migration_id),find_IP_by_ID(hosts, buffer.Migration_issuer), buffer.Placement)
					if TEST == 1: print command
					try:
						results = os.popen(command).readlines()
					except sys.stderr:
						print 'error'
					result = results[len(results)-1].strip('\n')
					if cmp(result, '0') == 0:
						# Package the message and send it
						reply=pickle.dumps(reply_unit)
						s.sendto(reply, address)

						# Send a copy to the server for measurement
						server_address = (config_dic['SERVER_IP'], int(config_dic['MULTICAST_PORT']))
						s.sendto(reply, server_address)
						
					else:
						print 'Migration failed'
						# Get configurations for the configure file
						config_dic=get_config()
						c = int(config_dic['COUNT'])
						modify_config('COUNT', str(c+1))

					modify_config('HOTSPOT', '0')
					# Get configurations for the configure file
					config_dic=get_config()
					COLD_LOCK = config_dic['COLD_LOCK'].split(':')
					# Delete the lock
					del COLD_LOCK[COLD_LOCK.index(str(buffer.Migration_id))]
					COLD_LOCK_item = ':'.join(COLD_LOCK)
					modify_config('COLD_LOCK', COLD_LOCK_item)
					s.close()
					exit()
		
		###############################################
		#####																					#####
		#####		Receive  MEASUREMENT REPLY message -- 15		#####
		#####																					#####
		###############################################
		if buffer.Message_type==15:
			if TEST == 1: print "save info for the PM into a file"
			fileHandel = open('PM_infos.txt','a')
			pickle.dump(buffer.PM_info, fileHandel)
			fileHandel.close()

		if not (int(sys.argv[1])== 1 or int(sys.argv[1]) == 14):

			exit_check()

except socket.timeout:
	print "Socket timeout"
	if int(sys.argv[1])==12:
		steal_fail() 
	s.close()
	exit()
except KeyboardInterrupt:
	print "User Press Ctrl+C,Exit"
except EOFError:
	print "User Press Ctrl+D,Exit"

s.close()
exit()

