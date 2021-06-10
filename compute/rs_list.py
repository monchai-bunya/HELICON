#!/usr/bin/python2
import os, socket, sys, struct, uuid, csv, time
from tools import get_config, modify_config


#--function: vm_info_generate
def rs_info_generate(rs):
	rs_multicast_group = ('224.3.29.73', 30001)

	# Create the datagram socket
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	# Set a timeout so the socket does not block indefinitely
	timeout = len(rs)
	s.settimeout(timeout)

	# Set the time-to-live for messages to 1
	ttl = struct.pack('b', 1)
	s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

	message = 'Request'
	s.sendto(message, rs_multicast_group)

	rs_info = {}
	n = 0
	try:
		
		rs_num = len(rs)
		# Receive/respond loop
		while True:
			(buf, address) = s.recvfrom(1024)  
			#print(buf)
			if not len(buf):
				continue
			array = buf.split(':')

			# The case that the vm is running in this host
			if array[0] in rs:
				rs_info[array[0]] = array[1]
				n += 1
				#print(rs_info)
			if n == rs_num:
				return rs_info

	except socket.timeout:
		return rs_info

def pm_info_generate(ip):
	#open vnf-ras file on compute node
	filepath = 'vnfrsml.csv'	
	with open(filepath, 'rb') as f:
		reader = csv.DictReader(f)
		rows = [row for row in reader if row['IP'] == ip]
	
	#get information from file and return interest variables
	for row in rows:
		print 'Get pm info: ' + row['latency'] + ' ' + row['packet_loss'] + ' ' + row['jitter'] + ' ' + row['normalized_load'] + ' ' + row['device_type']
			
	f.close()
	return row['latency'],row['packet_loss'],row['jitter'],row['normalized_load'],row['device_type']

def ras_list():
	rs = []
	config_dic = get_config()
	addresses = config_dic['PING_ADDRESS_RS']
	tcap = open('outtemprslist.csv','w')
	cap = open('time_transcode.txt','w')
	outfileml = config_dic['RS_FILENAME_ML']	
	mvout = 'mv outtemprslist.csv ' + outfileml

	#write header
	tcap.write('normalized_load')
	tcap.write(',')
	tcap.write('mem_utilization')
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
	tcap.write('vnf_load')
	tcap.write(',')
	tcap.write('IP')
	tcap.write(',')
	tcap.write('device_type')
	tcap.write('\n')

	#process each ip from list
	ad = addresses.split(',')
	for i in ad:
		rs.append(i)	

	#request information from raspi
	try:
		rs_info = rs_info_generate(rs)		
	except socket.error:
		exit()

	#get info from local vnf-ras file and combine with info from raspi and save
	for i in ad:
		latency,pkloss,jitter,vnfload,device_type = pm_info_generate(i)		
		if rs_info.has_key(i):
			#print '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t\tName:%s' % (rs_info[i].split()[0], rs_info[i].split()[1], latency, pkloss, jitter, rs_info[i].split()[2], rs_info[i].split()[3], vnfload, rs_info[i].split()[4], i)
			save_info = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (rs_info[i].split()[0], rs_info[i].split()[1], latency, pkloss, jitter, rs_info[i].split()[2], rs_info[i].split()[3], vnfload, i, rs_info[i].split()[4])
			tm_transcode = '%s' %(rs_info[i].split()[5])	
		else:
			#print '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t\tName:%s' % ('0.5', '50', latency, pkloss, jitter, '27', '50', vnfload, '11', i)
			save_info = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % ('0.5', '50', latency, pkloss, jitter, '27', '50', vnfload, i, '11')
			tm_transcode = '0'
		tcap.write(save_info)
		cap.write(tm_transcode)
	tcap.close()
	cap.close()
	os.system(mvout) 
#--------------------------------
## run the script
while True:
	ras_list()
	time.sleep(10)

