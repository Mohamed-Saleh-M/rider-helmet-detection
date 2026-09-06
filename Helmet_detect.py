import cv2
import numpy as np
import os
import imutils
from tensorflow.keras.models import load_model
import random
from datetime import datetime


os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
net = cv2.dnn.readNet("yolov3-custom_7000.weights", "yolov3-custom.cfg")
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
model = load_model('helmet-nonhelmet_cnn.h5')
#Locations : 143101 - Babowal Main 143108 - Attari State Highway 143108 - Bachiwind Ringroad 143119 - Bagga Toll Gate 143502 - Abdal State Highway
location = '143502 - Abdal State Highway'
save_dir = "C:/Users/FRIENDS.DESKTOP-1RIRFCP/Desktop/Helmet and Number Plate Detection and Recognition/Helmet Detector/Cases"
print("\t\tRIDERS HELMET SURVEILLANCE\n\nLOCATION : {}\nDATE : {}\n\nCASES LOG\n--------------".format(location,datetime.now().strftime("%d/%m/%y")))
print('SURVEILLANCE STREAMING STARTED AT',(datetime.now()).strftime("%H:%M:%S"))
cap = cv2.VideoCapture(r'{}.mp4'.format(location))
COLORS = [(0,255,0),(0,0,255)]
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
def helmet_or_nohelmet(helmet_roi):
	try:
		helmet_roi = cv2.resize(helmet_roi, (224, 224))
		helmet_roi = np.array(helmet_roi,dtype='float32')
		helmet_roi = helmet_roi.reshape(1, 224, 224, 3)
		helmet_roi = helmet_roi/255.0
		return int(model.predict(helmet_roi)[0][0])
	except:
			pass
ret = True
while ret:
    try:
      ret, img = cap.read()
      img = imutils.resize(img,height=500)
      height, width = img.shape[:2]
      blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
      net.setInput(blob)
      outs = net.forward(output_layers)
      confidences = []
      boxes = []
      classIds = []
      for out in outs:
          for detection in out:
              scores = detection[5:]
              class_id = np.argmax(scores)
              confidence = scores[class_id]
              if confidence > 0.3:
                  center_x = int(detection[0] * width)
                  center_y = int(detection[1] * height)
                  w = int(detection[2] * width)
                  h = int(detection[3] * height)
                  x = int(center_x - w / 2)
                  y = int(center_y - h / 2)
                  boxes.append([x, y, w, h])
                  confidences.append(float(confidence))
                  classIds.append(class_id)
      indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
      for i in range(len(boxes)):
          if i in indexes:
              x,y,w,h = boxes[i]
              color = [int(c) for c in COLORS[classIds[i]]]
              # green --> bike
              # red --> number plate
              if classIds[i]==0: #bike
                  helmet_roi = img[max(0,y):max(0,y)+max(0,h)//4,max(0,x):max(0,x)+max(0,w)]
              else: #number plate
                  x_h = x-60 
                  y_h = y-350
                  w_h = w+100
                  h_h = h+100
                  xhb = x_h-40 
                  yhb = y_h-50
                  whb = w_h+100 
                  hhb = h_h+600 
                  if y_h>0 and x_h>0:
                      numplate_num = img[y:y+h,x:x+w]
                      h_r = img[y_h:y_h+h_h , x_h:x_h +w_h]
                      bike = img[yhb:yhb+hhb , xhb:xhb+whb] 
                      c = helmet_or_nohelmet(h_r)
                      if c==1:
                        bike = bike if int(len(bike))>350 else img
                        number = random.randint(10,99)
                        now = datetime.now()
                        current_time = now.strftime("%d%m%y%H%M%S")
                        accnnumber = 'ACN'+current_time+str(number)
                        path = os.path.join(save_dir, location)
                        try:
                                os.mkdir(path)
                        except:
                                pass
                        path = os.path.join(path, accnnumber)
                        os.mkdir(path)
                        cv2.imwrite(path+'/numberplate.jpg',numplate_num)
                        cv2.imwrite(path+'/rider.jpg',h_r)
                        cv2.imwrite(path+'/bike.jpg',bike)
                        cv2.imwrite(path+'/rider_head.jpg',helmet_roi)
                        print("--Case "+accnnumber+" issued")
      if cv2.waitKey(1) == 27:
          break
    except:
            pass
print('SURVEILLANCE STREAMING ENDED AT',(datetime.now()).strftime("%H:%M:%S"),'\n--------------')
cap.release()
cv2.destroyAllWindows()
