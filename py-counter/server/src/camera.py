import cv2
import json,time,os
import numpy as np
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
import tensorflow as tf

class Cam:
   models={}
   def __init__(self,config=None):
      self.stop_it=True;
      conTime = self.connect(config)
      print("Spent time on import",conTime)
      
   def connect(self,config):
      t1=time.time()
      self.models['fire_r'] = tf.keras.models.load_model(config.PATHS['fire_r'])
      t2=time.time()
      return t2-t1;
   def encode(self,data):
      return cv2.imdecode(np.frombuffer(data, np.uint8), -1);
   def predict_fire(self,img):
      t1=time.time()
      resize = cv2.resize(img,(160,160))
      rgb = cv2.cvtColor(resize,cv2.COLOR_BGR2RGB)
      test = rgb[np.newaxis is None,:,:,:]
      predictions = self.models['fire_r'].predict(test)
      t2=time.time()
      h=0
      if predictions < -1:
         h=2
      elif predictions > -1 and predictions < 1.5:
         h=1
      return (h,t2-t1)