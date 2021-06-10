#!/usr/bin/python2
import os, sys
from datetime import datetime

#--------------------
if len(sys.argv) < 5:
  print "usage: " + sys.argv[0] + " VM_type VM_id dst_host Placement_group"
  exit()
else:
  vim = "openstack-site"
  nsd_name = "video_transcoder_nsd_" + sys.argv[4]
  id=sys.argv[2].split(":")
  if len(id)!=2:
    print "Format for VM_id: \'id:x\'"
    exit() 
  base_name = id[1].split("-")
  now = datetime.now().strftime('%Y_%m_%d_%H:%M:%S')
  instance_name = base_name[0] + '-' + 'place_' + now
  if cmp("xen",sys.argv[1].lower())==0:
    val="xm migrate -l %s %s" % (id[1], sys.argv[3])

  elif cmp("kvm",sys.argv[1].lower())==0:
    #val="virsh migrate --live %s qemu+ssh://%s/system" % (id[1], sys.argv[3])
    val = "osm ns-create --nsd_name %s --ns_name %s --vim_account %s" %(nsd_name, instance_name, vim)
  #elif cmp()
  #  val="osm"

  else:
    print "Not available. Please specify kvm or xen for VM_type."
    exit()
  #print val
  result=os.system(val)
  #print result



