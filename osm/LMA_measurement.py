#!/usr/bin/python2
Message_types={}
Message_types['1']='HELLO'
Message_types['2']='HELLO REPLY'
Message_types['3']='MIGRATION'
Message_types['4']='MIGRATION ACKNOWLEDGEMWNT'
Message_types['5']='HOTSPOT MESSAGE'
Message_types['6']='HOTSPOT REPLY'
Message_types['7']='WINNING BID ANNOUNCEMENT'
Message_types['8']='WINNING BID ACKNOWLEDGEMENT'
Message_types['9']='RESOURCE RELEASE'
Message_types['10']='STEAL BROADCAST'
Message_types['11']='STEAL BROADCAST REPLY'
Message_types['12']='STEAL ATTEMPT'
Message_types['13']='STEAL ATTEMPT ACKNOWLEDGEMENT'

class PM_info:
  def __init__(self):
    self.ID=0
    self.CPU_max=0
    self.CPU_current=0.0
    self.CPU_record = 0.0
    self.MEM_max=0
    self.MEM_used=0
    self.Traffic_Bytes=0
    self.Traffic_packets=0
    self.device_type=''
    self.normalized_load=0.0
    self.memtotal=0.0
    self.mem_utilization=0.0
    self.core_number=0
    self.vcpu_number=0
    self.cpu_speed=0.0
    self.cache_size=0.0
    self.latency=0.0
    self.packet_loss=0.0
    self.jitter=0.0
    self.bandwidth=0.0
    self.net_utilization=0.0
    self.placement_group=''
  
class VM_info:
  def __init__(self):
    self.ID=0
    self.Virtual_cores_num=0
    self.disk=0
    self.CPU_current=0.0
    self.CPU_record = 0.0
    self.MEM=0
    self.Page_dirty_rate=0
    self.IP_host=[]
    self.IP_rs=[]
    self.IP_ue=[]
    self.predict=0.0
    self.accept_dalay=0

class LVA_unit:
  def __init__(self):
    self.Source_node=0
    self.Destination_node=0
    self.Message_type=0
    self.Content=''
    self.Migration_id=0
    self.Migration_issuer=0
    self.Placement=''
    self.PM_info=PM_info()
    self.VM_info=[]
    self.RP_info=[]
    self.UE_info=[]

class RP_info:
  def __init__(self):
    self.ID=0
    self.IP=''    
    self.device_type=''
    self.normalized_load=0.0
    self.memtotal=0.0
    self.mem_utilization=0.0
    self.core_number=0
    self.vcpu_number=0
    self.cpu_speed=0.0
    self.cache_size=0.0
    self.latency=0.0
    self.packet_loss=0.0
    self.jitter=0.0
    self.bandwidth=0.0
    self.net_utilization=0.0

class UE_info:
  def __init__(self):
    self.ID=0
    self.IP=''    
    self.device_type=''
    self.normalized_load=0.0
    self.memtotal=0.0
    self.mem_utilization=0.0
    self.core_number=0
    self.vcpu_number=0
    self.cpu_speed=0.0
    self.cache_size=0.0
    self.latency=0.0
    self.packet_loss=0.0
    self.jitter=0.0
    self.bandwidth=0.0
    self.net_utilization=0.0
