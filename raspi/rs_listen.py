#!/usr/bin/python2
import socket, struct, os, uuid, time, thread
from sys_tools import load_stat, memory_stat, net_stat, cpu_core, vcpu, cpu_clock, get_ping_time

interface = 'wlp2s0'
# raspi 11, vnf = 21, ue = 31
device_type = '11'
process_name = 'from-thetav'
def rs_info_update():
	global record

	while True:

		#get first value for bandwidth
		net = net_stat(interface)
		start_time = time.time()
		bytes_sum1 = net['ReceiveBytes'] + net['TransmitBytes']

		#calculate core number
		core = cpu_core()

		#calculate load
		load = load_stat()
		norm_load = float(load['lavg_5'])/core
		#calculate memoey
		mems = memory_stat()
		mem_utilization = (mems['MemUsed']/mems['MemTotal'])*100

		#calculate cpu clock and cache
		#clock_sp, cache_sz = cpu_clock()

		#get second value for bandwidth and get band width
		net = net_stat(interface)
		end_time = time.time()
		bytes_sum2 = net['ReceiveBytes'] + net['TransmitBytes']
		bytes_diff = bytes_sum2 - bytes_sum1
		measure_time = end_time-start_time
		bandwidth = bytes_diff/measure_time
		net_utilization = (bandwidth/float(54))*100
		fd = open('transcode_time.txt','r')
		tmp = os.popen("ps -A").read()
		if process_name not in tmp[:]:
		   transcode_time = '0'
		else:
		   transcode_time = fd.read()
		#get all values in a variable
		record = '%s %s %s %s %s %s' % (norm_load, mem_utilization, bandwidth, net_utilization, device_type, transcode_time.strip())
		print(record)
		fd.close()
		time.sleep(5)
global record

thread.start_new_thread(rs_info_update,(),)
address = ('', 30001)
multicast_group = '224.3.29.73'
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
		hostname = val.readline().strip()
		message = '%s:%s' % (hostname,record)
		print(message)
		s.sendto(message,address)

except KeyboardInterrupt:
	print "User Press Ctrl+C,Exit"
except EOFError:
	print "User Press Ctrl+D,Exit"

s.close() 
exit()
