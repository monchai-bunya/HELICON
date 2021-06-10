#!/usr/bin/python

import cv2
import numpy as np
from PIL import Image
import threading
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import StringIO
import time, os, glob, sys
import requests, json, pprint

#Live Preview parameters
url = "http://192.168.1.1:80/osc/commands/execute"
headers = {'Content-type': 'application/json'}
body = json.dumps({"name": "camera.getLivePreview",
                "parameters": {}})

class CamHandler(BaseHTTPRequestHandler):

	def do_GET(self):
		if self.path.endswith('.mjpg'):
			self.send_response(200)
			self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
			self.end_headers()
                        response = requests.post(url, data=body, stream=True, headers=headers)
                        if response.status_code == 200:
                           print("Getting Live Video: 5GinFire\n")
                           f = open(measure_tra,'w')
			   start_time = time.time()
                           bytes=''
			   while True:
			      try:	
                                 				
                                 for block in response.iter_content(16384):
                                     bytes += block
                                     # Search the current block of bytes for the jpq start and end
                                     a = bytes.find('\xff\xd8')
                                     b = bytes.find('\xff\xd9')
                                     # If you have a jpg, display to Browser
                                     if a!=-1 and b!=-1:
                                        jpg = bytes[a:b+2]
                                        bytes= bytes[b+2:]
                                        img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)                      
					imgRGB=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
					jpg = Image.fromarray(imgRGB)
					tmpFile = StringIO.StringIO()
					jpg.save(tmpFile,'JPEG')
					self.wfile.write("--jpgboundary")
					self.send_header('Content-type','image/jpeg')
					self.send_header('Content-length',str(tmpFile.len))
					self.end_headers()
					jpg.save(self.wfile,'JPEG')
					#os.remove(being_processed)
                                        end_time = time.time()
                                 	#print "end = ", end_time
                                 	#print "Start = ", start_time
                                 	process_time = end_time-start_time
                                 	print "Process = ", process_time
					fd = open(measure_rl,'w')
                                        f.write('%3.15f\n' %(process_time))   
					fd.write('%3.2f\n' %(process_time))  
					fd.close()                             
                                 	start_time = time.time()
			      except KeyboardInterrupt:
				 break
			   return
                
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""

def main():
	#global capture
	#capture = cv2.VideoCapture(0)
        #capture.set(cv2.CV_CAP_PROP_FOURCC, cv2.CV_FOURCC(*'H264'))
        #capture.set(CV_CAP_PROP_FOURCC, CV_FOURCC(*'H264'))
	try:
                global measure_tra, measure_rl
                measure_tra = './' + sys.argv[1] + '/vdo_transcoding.txt'
                measure_rl = 'transcode_time.txt'
                if not os.path.exists(sys.argv[1]):
                   os.makedirs(sys.argv[1])
		server = ThreadedHTTPServer(('', 8880), CamHandler)
                #server = ThreadedHTTPServer(('', 8550), CamHandler)
		print "IP Camera started"
		server.serve_forever()
	except KeyboardInterrupt:
		#capture.release()
		server.socket.close()

if __name__ == '__main__':
	main()

