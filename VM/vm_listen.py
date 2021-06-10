#!/usr/bin/python2
import socket, struct, os, uuid, time, thread
from sys_tools import load_stat, memory_stat

port_all = '8880\|3141\|3142\|3143\|3144\|3145\|3146'
port_rs = '8880'
port_ue = '3141\|3142\|3143\|3144\|3145\|3146'
port_ue_list = ['3141','3142','3143','3144','3145','3146']
check = [',',';']

def vm_info_update():
	global record, chain, link
	k=5
	load_sum = 0
	dirty_sum = 0	
	while(k>0):
		load_sum += float(load_stat()['lavg_5'])
		dirty_sum += float(memory_stat()['Dirty'])
		k -= 1

	L_t = load_sum/5
	D_t = dirty_sum/5
	l_t = float(load_stat()['lavg_5'])
	d_t = float(memory_stat()['Dirty'])
	record = '%s %s %s %s' % (L_t, l_t, D_t, d_t)

	while True:
		L_t = 0.2*l_t + 0.8*L_t
		D_t = 0.2*d_t + 0.8*D_t
		l_t = round(float(load_stat()['lavg_5']), 2)
		d_t = round(float(memory_stat()['Dirty']), 3)
		L_t = round(L_t, 2)
		D_t = round(D_t, 3)
		record = '%s %s %s %s' % (L_t, l_t, D_t, d_t)
		chain = []
		for i in range(3):			
			#get all the connection on this VM
			#select connection with same pid
			command1 = "netstat -tnp | grep '" + port_all + "' | grep 'python' |  awk '{print $7}' | cut -d '/' -f1 | sort | uniq -d"		
			val_pid = os.popen(command1)
			connect_pid = val_pid.read().strip()
			
			# split the matching into Raspi and UE
			if connect_pid:
				pid_p = connect_pid.split('\n')
				for con_pid in pid_p:
					chain1 = ''
					#get Raspi IP
					command2 = "netstat -tnp | grep '" + con_pid + "' | grep '" + port_rs + "' | awk '{print $4, $5}'" 
					val_con1 = os.popen(command2)
					val_con_rs = val_con1.read().strip()
					sin_con_rs = val_con_rs.split()
					for sin_con1 in sin_con_rs:
						sin1 = sin_con1.split(':')
						if sin1[1] == port_rs:
							if not ',' in chain1:						
								chain1 += sin1[0] + ',' 
							#print 'Raspi: ' + sin1[0]
					#print 'Raspi: ' + chain1	
					#get UE IP
					#command3 = "netstat -tnp | grep '" + con_pid + "' | grep '" + port_ue + "' | awk '{print $4, $5}'" 
					command3 = "netstat -tnp | grep '" + con_pid + "' | grep '" + port_ue + "' | awk '{print $5}'"
					val_con2 = os.popen(command3)
					val_con_ue = val_con2.read().strip()
					sin_con_ue = val_con_ue.split()
					for sin_con2 in sin_con_ue:	
						sin2 = sin_con2.split(':')
						#if sin2[1] in port_ue_list:
						if not ';' in chain1:
							chain1 += sin2[0] + ';'
							#print 'UE: ' + sin2[0]
					#print 'Raspi + UE: ' + chain1
	
					#if contain both Raspi and User ip
					if any(x in chain1 for x in check):		
					#if ',' and ';' in chain1:						
						chain.append(chain1)
						#print 'Raspi + UE after: ' + chain1							
					else:
						chain.append(i)

			else:
				chain.append(i)
			time.sleep(1)
		if chain[0] == chain[1] == chain[2]:
			link = chain[0]			
			print 'OK can save: ' + link			
		else:
			link = ''
			print 'Not OK cannot save'


global record, chain, link

thread.start_new_thread(vm_info_update,(),)
address = ('', 30000)
multicast_group = '224.3.29.72'
measure_rl1 = 'receive_time.txt'
measure_rl2 = 'process_time.txt'
process_name = 'face-nvr'
# Create the socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
# Bind to the server address
s.bind(address)

# Tell the operating system to add the socket to the multicast group on all interfaces.
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

try:
	# Receive/respond loop
	while True:
		(buf, address) = s.recvfrom(1024)  

		if not len(buf):
			continue

		print "\n***********************************"
		print "Received from", address
		print buf

		val = os.popen("hostname -I | awk '{print $1}'")
		#val = os.popen("hostname")
		hostname = val.readline().strip()
		fd1 = open(measure_rl1,'r')
		fd2 = open(measure_rl2,'r')
		tmp = os.popen("ps -A").read()
		if process_name not in tmp[:]:
		   receive_time = '0'
		   process_time = '0'
		else:
		   receive_time = fd1.read()
		   process_time = fd2.read()
		message = '%s:%s:%s:%s:%s' % (hostname,record,link,receive_time.strip(),process_time.strip())
		print 'To send: ' + message
		s.sendto(message,address)

except KeyboardInterrupt:
	print "User Press Ctrl+C,Exit"
except EOFError:
	print "User Press Ctrl+D,Exit"

s.close() 
exit()
