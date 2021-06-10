#!/usr/bin/python2
import os, socket, sys, struct, uuid, subprocess
#---function: status_judge
def status_judge(sta):
  s=0
  while s<6:
    if cmp("-",sta[s:s+1])!=0:
      return status_info(s)
    s=s+1

#---function: status_info
def status_info(value):
  if value==0:
    return "running"
  elif value==1:
    return "blocked"
  elif value==2:
    return "paused"
  elif value==3:
    return "crashed"
  elif value==4:
    return "dying"
  else: return "shutdown"

#--function: vm_info_generate
def vm_info_generate(vms):
	vm_multicast_group = ('224.3.29.72', 30000)
	# Create the datagram socket
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# Set a timeout so the socket does not block indefinitely
	#timeout = 20
	timeout = len(vms)
	s.settimeout(timeout)
	# Set the time-to-live for messages to 1
	ttl = struct.pack('b', 1)
	s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

	message = 'Request'
	s.sendto(message, vm_multicast_group)
	vm_info = {}
	n = 0
	try:
		#if cmp("xen",sys.argv[1].lower())==0:
		#	vm_num = len(vms) - 1
		#else:
		vm_num = len(vms)
		# Receive/respond loop
		while True:			
			(buf, address) = s.recvfrom(1024) 					
			if not len(buf):
				continue
			array = buf.split(':')	
			cap1 = open('time_receive.txt','w')
			cap2 = open('time_process.txt','w') 
			if array[3]:
				tm_receive = array[3]
			else:
				tm_receive = '0'
			if array[4]:
				tm_process = array[4]
			else:
				tm_process = '0'
			cap1.write(tm_receive)
			cap2.write(tm_process)
			cap1.close()
			cap2.close()
			# The case that the vm is running in this host
			if array[0] in vms:
				vm_info[array[0]] = array[1]
				if array[2]:
					array[2] = array[2].replace(","," ")
					array[2] = array[2].replace(";"," ")
					vm_info['link'] = array[0] + ' ' + array[2]
				n += 1
			if n == vm_num:
				return vm_info
			#print array[0]
			#print vm_info
			'''
			print "VM_id\t\tVM_type\tVM_status\tVCPUs\tMem\tDirty\tLoad\tLoad_record\tDescription\tNumber_of_connection\t(Host_IP/Raspi_IP/UE_IP)"

			
			if vm_info.has_key('link'):
				member = len(vm_info['link'].split())
				if member % 3 == 0:
					print '%s\tKvm\t%s\t%s\t%s\t%s\t%s\t%s\t\tName:%s\t\t%s\t\t%s' % (array[0], 'array[2]',  'CPU(s)', 'mem', vm_info[array[0]].split()[2], vm_info[array[0]].split()[0], vm_info[array[0]].split()[1], 'array[1]', member/3, vm_info['link'])
			
			
			print '%s\tKvm\t%s\t%s\t%s\t%s\t%s\t%s\t\tName:%s\t\t%s\t\t%s' % (array[0], 'array[2]',  'CPU(s)', 'mem', vm_info[array[0]].split()[2], vm_info[array[0]].split()[0], vm_info[array[0]].split()[1], 'array[1]', 'NaN', "vm_info['link']")
			#print(vm_info)
			
			if vm_info.has_key('link'):
				print(vm_info['link'])
				print(len(vm_info['link'].split()))
				member = len(vm_info['link'].split())
				print 'Member1: %d' %(member)
				if member % 3 == 0:
					print 'Member2: %s' %(member/3)

			
				print(vm_info['link'].split(','))
				link_maps = vm_info['link'].split(',')
				for link_map in link_maps:
					print(link_map.replace(";",""))	
			'''
	except socket.timeout:
		return vm_info
'''
#---function: xen_list
def xen_list():
	val = os.popen("xm list | sed -e \"1d\" ")
	results = val.readlines()
	vms = []
	for result in results:
		vms.append(result.split()[0]) 
	try:
		vm_info = vm_info_generate(vms)
	except socket.error:
		print 'socket error'
		exit()

	print "VM_id\tVM_type\tVM_status\tVCPUs\tMem\tDirty\tLoad\tLoad_record\tDescription"
	for result in results:
		array = result.split()
		try:
			if vm_info.has_key(array[0]):
				print '%s\tXen\t%s\t\t%s\t%s\t%s\t%s\t%s\t\tName:%s' % (array[1], status_judge(array[4]),  array[3], array[2], vm_info[array[0]].split()[2], vm_info[array[0]].split()[0], vm_info[array[0]].split()[1], array[0])
			else:
				print '%s\tXen\t%s\t\t%s\t%s\t%s\t%s\t%s\t\tName:%s' % (array[1], status_judge(array[4]),  array[3], array[2], 'NaN', 'NaN', 'NaN', array[0])
		except IndexError:
			continue
'''
#---function: kvm_list
def kvm_list():
	#val = os.popen("virsh list | sed -e \"1,2d\" | sed /^$/d")
	#should call source admin-openrc in terminal before
	host = os.popen("hostname")
	hostname = host.read().strip()
	command1 = "nova list --host %s | grep 'Running' | awk '{print $12}' | cut -d '=' -f2" %hostname
	val1 = os.popen(command1)
	#val = os.popen("virsh list | sed -e \"1,2d\" | sed /^$/d")
	results = val1.readlines()
	if len(results) == 0: 
		exit()
	vms = []
	for result in results:
		vms.append(result.strip())		
		#vms.append(result.split()[1])
	try:
		#vm_info = vm_info_generate('192.168.1.154')
		vm_info = vm_info_generate(vms)
	except socket.error:
		exit()

	command2 = "nova list --host %s | grep 'Running' | awk '{print $4, $12}'" %hostname
	val2 = os.popen(command2)
	results2 = val2.readlines()
	if len(results2) == 0: 
		exit()

	print "VM_id\t\tVM_type\tVM_HD\tVCPUs\tMem\tDirty\tLoad\tLoad_record\tDescription\t\t\tNumber_of_connection\t(Host_IP/Raspi_IP/UE_IP)"

	for result2 in results2:
		array = result2.split()		
		#command = "virsh dominfo %s" % array[1]
		command3 = "nova show %s | awk '{print $2, $4}'" % array[0]
		val3 = os.popen(command3)
		records = val3.readlines()
		infos = {}
		for record in records:
			record = record.strip('\n')
			#k_v = record.split(':')
			k_v = record.split()
			if len(k_v) != 2: continue
			infos[k_v[0].strip()] = k_v[1].strip()
		#mem = int(infos['Max memory'].split()[0])/1024
		#try:
		ips = array[1].split('=')[1]
		#if vm_info.has_key(array[1]):
		if vm_info.has_key(ips):
			if vm_info.has_key('link'):
				member = len(vm_info['link'].split())
				if member % 3 == 0:					
					print '%s\tKvm\t%s\t\t%s\t%s\t%s\t%s\t%s\t\tIP:%s\t%s\t\t%s' % (array[0], infos['flavor:disk'],  infos['flavor:vcpus'], infos['flavor:ram'], vm_info[ips].split()[2], vm_info[ips].split()[0], vm_info[ips].split()[1], ips, member/3, vm_info['link'])
				else:
					print '%s\tKvm\t%s\t\t%s\t%s\t%s\t%s\t%s\t\tIP:%s\t%s' % (array[0], infos['flavor:disk'],  infos['flavor:vcpus'], infos['flavor:ram'], vm_info[ips].split()[2], vm_info[ips].split()[0], vm_info[ips].split()[1], ips, 'NaN')
			else:
				print '%s\tKvm\t%s\t\t%s\t%s\t%s\t%s\t%s\t\tIP:%s\t%s' % (array[0], infos['flavor:disk'],  infos['flavor:vcpus'], infos['flavor:ram'], vm_info[ips].split()[2], vm_info[ips].split()[0], vm_info[ips].split()[1], ips, 'NaN')
		else:
			print '%s\tKvm\t%s\t\t%s\t%s\t%s\t%s\t%s\t\tIP:%s\t%s' % (array[0], infos['flavor:disk'],  infos['flavor:vcpus'], infos['flavor:ram'], 'NaN', 'NaN', 'NaN', ips, 'NaN')

		
		#except IndexError:
			#continue
#--------------------------------
if len(sys.argv) < 2:
  print "usage: " + sys.argv[0] + " VM_type"
  exit()
elif len(sys.argv) == 2:
  #if cmp("xen",sys.argv[1].lower())==0:
  #  xen_list()
  if cmp("kvm",sys.argv[1].lower())==0:
    kvm_list()
    #vm_info_generate('192.168.40.21')
#else: xen_list()
