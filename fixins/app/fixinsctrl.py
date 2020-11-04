import pysony
import board, neopixel
import time
import urllib.request as req
import RPi.GPIO as GPIO
from pathlib import Path

class FixtureInspectorController:
  QX_ADDR = "http://192.168.122.1:8080"

  search = None
  cameras = None
  camera = None

  pixel_pin = board.D18
  pixels = None
  num_pixels = 10

  halfstep = 0
  control_pins = [22, 24, 23, 25]
  halfstep_seq = [
    [1,0,0,0],
    [1,1,0,0],
    [0,1,0,0],
    [0,1,1,0],
    [0,0,1,0],
    [0,0,1,1],
    [0,0,0,1],
    [1,0,0,1]
  ]

  def __init__(self):
    self.setupCam()
    # self.setupNeopixel()
    self.setupStepmotor()

  # def __del__(self):
  #   self.setupNeopixel()
  #   self.pixels.fill((0, 0, 0, 0))
  #   GPIO.cleanup()

  def setupCam(self):
    # print("Searching for camera...")

    # self.search = pysony.ControlPoint(interface="wlan0")
    # self.cameras = self.search.discover()

    # if len(self.cameras):
    #   print("Found: %s" % self.cameras[0])
    #   print("")
    #   self.camera = pysony.SonyAPI(QX_ADDR=self.cameras[0])
    # else:
    #   print("No camera found, aborting")
    #   quit()
    self.camera = pysony.SonyAPI(QX_ADDR=self.QX_ADDR)

    self.camera.startRecMode()
    time.sleep(5)

    self.camera.setFocusMode('AF-S')
    self.camera.setPostviewImageSize('Original')
    self.camera.setFNumber('22')
    self.camera.setIsoSpeedRate('100')
    self.camera.setShutterSpeed('1/10')
    self.camera.setTouchAFPosition([50.0, 50.0])


  def setupStepmotor(self):
    for pin in self.control_pins:
      GPIO.setup(pin, GPIO.OUT)
      GPIO.output(pin, 0)
  
  # 1 halfstep is 0.9 degree
  # 100 halfstep is 90 degree
  def Stepmotor(self, step):
    for i in range(abs(step)):
      for pin in range(4):
        GPIO.output(self.control_pins[pin], self.halfstep_seq[self.halfstep][pin])

      if step > 0:
        self.halfstep += 1
        if self.halfstep == 8:
          self.halfstep = 0
      else:
        self.halfstep -= 1
        if self.halfstep == -1:
          self.halfstep = 7

      time.sleep(0.001)
    
  def Stepmotor_idle(self):
    for pin in range(4):
      GPIO.output(self.control_pins[pin], GPIO.LOW)

  def resetStep(self):
    self.halfstep = 0

  def TakePicture(self, filename="image.jpg"):
    res = self.camera.actTakePicture()
    res = req.urlretrieve(res['result'][0][0].replace('\/', '/'), filename)

if __name__ == '__main__':
  filename = ".jpg"

  fictrl = FixtureInspectorController()
  
  fictrl.pixelOn()

  st0 = time.time()
  for i in range(100):
    st1 = time.time()
    fictrl.camera.setTouchAFPosition([50.0, 50.0])
    for j in range(4):
      print('i : ' + str(i) + ' j : ' + str(j))
      st2 = time.time()
      res = fictrl.camera.actTakePicture()
      print('picture taken : ' + str(time.time()-st2))
      res = req.urlretrieve(res['result'][0][0].replace('\/', '/'),
      str(Path.cwd()) + "/temp_" + str(100).zfill(4) + "/" + str(j).zfill(3) + '_' + str(i).zfill(3) + filename)
      print('image download : ' + str(time.time()-st2))
      fictrl.Stepmotor(-100)
      print('motor rotated : ' + str(time.time()-st2))
    print('a cycle done : ' + str(time.time()-st1))
  fictrl.pixelOff()
