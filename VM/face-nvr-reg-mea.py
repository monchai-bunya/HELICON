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

client_ip = sys.argv[1]
server_port = int(sys.argv[2])
filename = sys.argv[3] + '.mjpg'
url = 'http://' + client_ip + ':8880/cam.mjpg'
#url='http://192.168.108.159:8880/cam.mjpg'
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
face_recognizer = cv2.face.LBPHFaceRecognizer_create()
face_recognizer.read('train4.yml')
subjects = ["", "Monchai", "Teresa", "Aloizio", "Hamid"]
path = './saved/'
videos = './videos/'
measure_rec = './' + sys.argv[4] + '/vnf_received.txt'
measure_pro = './' + sys.argv[4] + '/vdo_processing.txt'
measure_rlc = 'receive_time.txt'
measure_rld = 'process_time.txt'
#create folder if not exist
if not os.path.exists(path):
   os.makedirs(path)
if not os.path.exists(videos):
   os.makedirs(videos)
if not os.path.exists(sys.argv[4]):
   os.makedirs(sys.argv[4])
# Define the codec and create VideoWriter object
#fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
#output = cameraname + '.avi'
#out = cv2.VideoWriter(output, fourcc, 6, (1024,512))

class CamHandler(BaseHTTPRequestHandler):
        
        def do_HEAD(s):
            s.send_response(200)
            s.send_header("Content-type", "text/html")
            s.end_headers()
                    
	def do_GET(s):
	    s.send_response(200)
	    s.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
	    s.end_headers()
            frame_count = 1
	    while True:
		   try: 
                        #con_start_time = time.time()  
                        f1 = open(measure_rec,'w')
                        f2 = open(measure_pro,'w')
                        #f1 = open('vnf_received.txt','w')
                        #f2 = open('vdo_processing.txt','w')
                 	start_time = time.time()
                        stream=urllib.urlopen(url)
                        #con_end_time = time.time()
                        #con_time = con_end_time - con_start_time
                        #print "Connection time = ", con_time                       
			
                        #stream = open(filename, 'rb')
                        #start_time = time.time()
                        bytes=''
                        now_time = strftime("%Y%b%d%H%M%S", localtime())
                        cameraname = sys.argv[3] + '_' + now_time                        
                        #fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
                        #output = path + cameraname + '.avi'
                        #out = cv2.VideoWriter(output, fourcc, 6, (1024,512))
                        #out = cv2.VideoWriter(output, fourcc, 6, (640,480))
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
                                 
                                 # face detection
                                 gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
                                 faces = face_cascade.detectMultiScale(gray,1.2,5)
                                 for (x,y,w,h) in faces:                                     
                                     roi_gray = gray[y:y+h,x:x+w]
                                     roi_color = img[y:y+h,x:x+w]
                                     #predict the image using our face recognizer
                                     label, conf = face_recognizer.predict(roi_gray)
                                     #print(conf)
                                     cv2.rectangle(img, (x,y), (x+w, y+h), (255,0,0),2)
                                     if conf < 120:
                                        #get name of respective label returned by face recognizer
                                        label_text = subjects[label]                                     
                                        cv2.putText(img, label_text, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
                                     eyes = eye_cascade.detectMultiScale(roi_gray)
                                     for (ex,ey,ew,eh) in eyes:
                                         cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh), (0,255,0),2)
                                 #cv2.imshow('image',img)
                                 '''
                                 if frame_count > 360:
                                    shutil.move(output, videos)
                                    now_time = strftime("%Y%b%d%H%M%S", localtime())
                                    cameraname = sys.argv[3] + '_' + now_time                                    
                                    fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
                                    output = path + cameraname + '.avi'
                                    out = cv2.VideoWriter(output, fourcc, 6, (1024,512)) 
                                    #out = cv2.VideoWriter(output, fourcc, 6, (640,480))                                   
                                    frame_count = 1
                                 out.write(img)
                                 '''
			         imgRGB=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
			         jpg = Image.fromarray(imgRGB)
			         tmpFile = StringIO.StringIO()
			         jpg.save(tmpFile,'JPEG')
			         s.wfile.write("--jpgboundary")
			         s.send_header('Content-type','image/jpeg')
			         s.send_header('Content-length',str(tmpFile.len))
                                 s.end_headers()
			         jpg.save(s.wfile,'JPEG')
                                 frame_count += 1
                                 end_time = time.time()
                                 #print "end = ", end_time
                                 #print "Start = ", start_time
                                 process_time = end_time-frame_time
                                 #process_time = end_time-start_time
                                 received_time = frame_time-start_time
                                 print "Received = ", received_time
                                 print "Process = ", process_time 
                                 fc = open(measure_rlc,'w')
                                 fd = open(measure_rld,'w')
                                 f1.write('%3.15f\n' %(received_time))
                                 f2.write('%3.15f\n' %(process_time))  
                                 fc.write('%3.2f\n' %(received_time)) 
                                 fd.write('%3.2f\n' %(process_time))  
                                 fc.close()  
                                 fd.close()                               
                                 start_time = time.time() 
		   except KeyboardInterrupt:
			break
	    return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""

def main():
	
	try:
		server = ThreadedHTTPServer(('', server_port), CamHandler)
		print "5Ginfire Live Camera Demo Server started"
		server.serve_forever()
	except KeyboardInterrupt:
		server.socket.close()

if __name__ == '__main__':
	main()

