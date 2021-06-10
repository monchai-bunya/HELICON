#!/usr/bin/python2
import os, multiprocessing, subprocess, platform, re

# Function to get load infos from proc file: loadavg
def load_stat():
    loadavg = {}
    f = open("/proc/loadavg")
    con = f.read().split()
    f.close()
    loadavg['lavg_1']=con[0]
    loadavg['lavg_5']=con[1]
    loadavg['lavg_15']=con[2]
    loadavg['nr']=con[3]
    loadavg['last_pid']=con[4]
    return loadavg

# Function to get memory infos from proc file: meminfo
def memory_stat():
    mem = {}
    f = open("/proc/meminfo")
    lines = f.readlines()
    f.close()
    for line in lines:
        if len(line) < 2: continue
        name = line.split(':')[0]
        var = line.split(':')[1].split()[0]
        mem[name] = long(var) / 1024.0
    mem['MemUsed'] = mem['MemTotal'] - mem['MemFree'] - mem['Buffers'] - mem['Cached']
    return mem  

# Function to get network infos from proc file: net/dev
def net_stat(inf_name):  
    net = []  
    f = open("/proc/net/dev")  
    lines = f.readlines()  
    f.close()  
    for line in lines[2:]:  
        con = line.split()  
 
        intf = dict(  
            zip(  
                ( 'interface','ReceiveBytes','ReceivePackets',  
                  'ReceiveErrs','ReceiveDrop','ReceiveFifo',  
                  'ReceiveFrames','ReceiveCompressed','ReceiveMulticast',  
                  'TransmitBytes','TransmitPackets','TransmitErrs',  
                  'TransmitDrop', 'TransmitFifo','TransmitFrames',  
                  'TransmitCompressed','TransmitMulticast' ),  
                ( con[0].rstrip(":"),int(con[1]),int(con[2]),  
                  int(con[3]),int(con[4]),int(con[5]),  
                  int(con[6]),int(con[7]),int(con[8]),  
                  int(con[9]),int(con[10]),int(con[11]),  
                  int(con[12]),int(con[13]),int(con[14]),  
                  int(con[15]),int(con[16]), )  
            )  
        )
        if cmp(intf['interface'],inf_name) == 0: return intf
    return False 

def cpu_core():
    num_core = multiprocessing.cpu_count()
    return num_core

def vcpu():
    vcpu_count = 0
    dom_ids = os.popen("virsh list | awk '{print $1}' | grep -oIE '[0-9]*'")
    for dom_id in dom_ids:
        virsh_command = 'virsh dominfo ' + dom_id
        dom_info = subprocess.check_output(virsh_command, shell=True).strip()
        for dom in dom_info.split("\n"):
            if "CPU(s)" in dom:
                vcpus = dom.strip().split()
                vcpu_count += int(vcpus[1])                
    return vcpu_count

def cpu_clock():
    command = "cat /proc/cpuinfo"
    all_info = subprocess.check_output(command, shell=True).strip()
    for line in all_info.split("\n"):
        if "cpu MHz" in line:
            clocks = line.strip().split()
            clock_speed = float(clocks[3])
        if "cache size" in line:
            caches = line.strip().split()
            cache_size = float(caches[3])
    return clock_speed, cache_size
    #raspi follow this command get only cpu speed not cache size
    #command = "cat sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq"
    #all_info = subprocess.check_output(command, shell=True)
    #return all_info

def get_ping_time(host):
    ip = host
    interval = 0.5
    count = 10
    time_out = 20
    jitters = []
    jitter_difs = 0
    try:
        ping_command = 'ping -i ' + str(interval) + ' -c ' + str(count) + ' -w ' + str(time_out) + ' ' + ip
        ping_info = subprocess.check_output(ping_command, shell=True).strip()
        for p in ping_info.split("\n"):
            if "time=" in p:
                jits = p.strip().split() 
                jitt = float(jits[6].replace("time=",""))
                jitters.append(jitt)       
            if "packet loss" in p:
                packets = p.strip().split()
                packet_loss = float(packets[5].replace("%",""))
            if "min/avg/max/mdev" in p:
                pings = p.strip().split()
                ping_times = re.split('/', pings[3])
                ping_time = float(ping_times[1])    
        for i in range(len(jitters)-1):
            jitter_diff = abs(jitters[i] - jitters[i+1])
            jitter_difs += jitter_diff        
        jitter = jitter_difs/len(jitters)
    except Exception:
        ping_time = 1000
        packet_loss = 100
        jitter = 1000
        pass       
    return ping_time, packet_loss, jitter

#a = ['127.0.0.1','172.23.1.157','172.23.255.254']
#addresses = config_dic['PING_ADDRESS']
#ad = addresses.split(',')
#for i in a:
#load = load_stat()
#mems = memory_stat()
#net = net_stat('wlp2s0')
#core = cpu_core()
#vcpu = vcpu()
#clock_sp, cache_sz = cpu_clock()
#   print 'Pinging', i
#   ping_tm,pac_ls,jit = get_ping_time(i)   
#print(load['lavg_5'])
#print(mems['MemTotal'])
#print(net['ReceiveBytes'])
#print(net['TransmitBytes'])
#print(core)
#print(vcpu)
#print(clock_sp)
#print(cache_sz)
#   print(ping_tm)
#   print(pac_ls)
#   print(jit)
