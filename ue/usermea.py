#!/usr/bin/python

import cv2
import numpy as np
from PIL import Image
import threading
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import StringIO
import time
from time import gmtime, strftime, localtime
import urllib
import sys, os, shutil
#from face_reg import detect_face, draw_rectangle, draw_text, predict

#server_port = int(sys.argv[2])
#filename = sys.argv[3] + '.mjpg'

client_ip = sys.argv[1]
client_port = sys.argv[2]
url = 'http://' + client_ip + ':' + client_port + '/cam.mjpg'
measure_req = './' + sys.argv[3] + '/vdo_requesting.txt'
measure_rec = './' + sys.argv[3] + '/vdo_requesting_received.txt'
measure_rl = 'request_time.txt'
if not os.path.exists(sys.argv[3]):
   os.makedirs(sys.argv[3])
#url='http://192.168.108.159:8880/cam.mjpg'
frame_count = 0
#con_start_time = time.time()  
f1 = open(measure_req,'w')
#f2 = open(measure_rec,'w')
start_time = time.time()                 
stream=urllib.urlopen(url)
#con_end_time = time.time()
#con_time = con_end_time - con_start_time
#print "Connection time = ", con_time
#stream = open(filename, 'rb')
#start_time = time.time()
bytes=''
#now_time = strftime("%Y%b%d%H%M%S", localtime())
#cameraname = sys.argv[3] + '_' + now_time                        
           
while True:
      #start_time = time.time()
      bytes+=stream.read(1024)
      a = bytes.find('\xff\xd8')
      b = bytes.find('\xff\xd9')
      #print "a = ", a
      #print "b = ", b
      if a!=-1 and b!=-1:
          frame_time = time.time()
          jpg = bytes[a:b+2]
          bytes= bytes[b+2:]
          img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
          #if not img is None: continue
          #predicted_img = predict(img)
          #cv2.imshow('image',img)
          frame_count += 1
          end_time = time.time()
          #print "End = ", end_time
          #print "Start = ", start_time
          received_time = frame_time - start_time
          request_time = end_time - start_time
          #process_time = end_time-start_time
          #print "Received = ", received_time
          print "Request = ", request_time
          #f2.write('%3.15f\n' %(received_time))
          fd = open(measure_rl,'w')
          f1.write('%3.15f\n' %(request_time))
          fd.write('%3.2f\n' %(request_time))  
          fd.close() 
          start_time = time.time()
