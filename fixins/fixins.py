import os, sys, time, socket, select, queue
from pathlib import Path
from functools import wraps, update_wrapper
from datetime import datetime
from io import BytesIO
import urllib.request as req

from flask import Flask, render_template, url_for, request, redirect, make_response, Response
from flask_socketio import SocketIO, emit
import pysony, board, neopixel
from PIL import Image
import RPi.GPIO as GPIO
import numpy as np
from sklearn.decomposition import PCA

sys.path.append('/home/pi/fixtureinspector/fixins/bCAPClient')
sys.path.append('/home/pi/fixtureinspector/fixins')

from bCAPClient import bcapclient as BCAPClient


camera = None
lot_number = 0
code = 0
serial = 0
ng_val = 0

factor = 1.1

post_view_image_size = '2M'

threads = [None, None, None, None, None, None]
angles = [0.0, 0.0, 0.0, 0.0, 0.0]

def camera_init():
  global camera
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
  camera = pysony.SonyAPI(QX_ADDR="http://192.168.122.1:8080")

  camera.startRecMode()
  time.sleep(5)

  camera.setExposureMode('Manual')
  camera.setFocusMode('AF-S')
  camera.setPostviewImageSize(post_view_image_size)
  camera.setFNumber('22')
  camera.setIsoSpeedRate('100')
  camera.setShutterSpeed('1/20')
  camera.setTouchAFPosition([50.0, 50.0])

# bcapclient = None
# hCtrl = None
# FHand51 = 0
# FHand52 = 0

def compensate():
  # global bcapclient, hCtrl, FHand51, FHand52
  global angles
  host = '192.168.150.100'
  port = 5007
  timeout = 2000

  bcapclient = BCAPClient.BCAPClient(host, port, timeout)

  bcapclient.service_start("")

  Name = ""
  Provider = "CaoProv.DENSO.VRC"
  Machine = "localhost"
  Option = ""

  hCtrl = bcapclient.controller_connect(Name, Provider, Machine, Option)

  FHand51 = bcapclient.controller_getvariable(hCtrl, "F51", "")
  FHand52 = bcapclient.controller_getvariable(hCtrl, "F52", "")

  bcapclient.variable_putvalue(FHand51, -float((angles[2]+angles[4])/2))
  bcapclient.variable_putvalue(FHand52, -float((angles[1]+angles[3])/2))

  bcapclient.variable_release(FHand51)
  bcapclient.variable_release(FHand52)

  bcapclient.controller_disconnect(hCtrl)

  bcapclient.service_stop()


plasma_pin = 23
GPIO.setmode(GPIO.BCM)            # choose BCM or BOARD  
GPIO.setup(plasma_pin, GPIO.OUT) # set a port/pin as an output   

def nocache(view):
  @wraps(view)
  def no_cache(*args, **kwargs):
    response = make_response(view(*args, **kwargs))
    response.headers['Last-Modified'] = datetime.now()
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response
  return update_wrapper(no_cache, view)

__author__ = 'JaewonAC'
HOST = "0.0.0.0"
PORT = 80

app = Flask(__name__)
app.config['SECRET_KEY'] = 'brf89hy2349hg8f9r8239hjugv0amz'
app.config['DEBUG'] = True
app.get_frame_handle = None

#turn the flask app into a socketio app
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

@app.route('/')
@app.route('/index')
@nocache
def index():
  return render_template('index.html')

@app.route('/inspect')
@nocache
def inspect():
  global lot_number, code, serial
  if lot_number == 0:
    return render_template('inspect.html')
  else:
    return render_template('inspect.html',
                           lot_number=lot_number,
                           code=code,
                           serial=serial,
                           image1=str(lot_number) + '_' + str(code) + '_' + str(serial) + '_001.jpg',
                           image2=str(lot_number) + '_' + str(code) + '_' + str(serial) + '_002.jpg',
                           image3=str(lot_number) + '_' + str(code) + '_' + str(serial) + '_003.jpg',
                           image4=str(lot_number) + '_' + str(code) + '_' + str(serial) + '_004.jpg',
                           image5=str(lot_number) + '_' + str(code) + '_' + str(serial) + '_005.jpg')

def load_image(image_url, filename, lot_number, code, serial, shoot_num):
  global factor
  res = req.urlopen(image_url)
  img = Image.open(BytesIO(res.read()))

  if int(shoot_num) < 5:
    gray = np.array(img.convert('L'))
    pca = PCA()
    if post_view_image_size == 'Original':
      pca.fit(np.argwhere(gray[600:2900, 2000:gray.shape[1]-2001] > 30))
    elif post_view_image_size == '2M':
      pca.fit(np.argwhere(gray[210:860, 600:gray.shape[1]-601] > 30))
    else:
      pca.fit(np.argwhere(gray > 30))
    # angle = np.arcsin(pca.components_[0][1])*180
    angle = str(pca.components_[0][0]) + " " + str(pca.components_[0][1]) + " " + str(pca.components_[1][0]) + " " + str(pca.components_[1][1])
    # angle = str(np.arctan(pca.components_[0][1]/pca.components_[0][0])*180/np.pi) + " " + str(np.arctan(pca.components_[1][1]/pca.components_[1][0])*180/np.pi)
    length = float(code[2:4])
    if (int(shoot_num) == 2) | (int(shoot_num) == 3):
      angles[int(shoot_num)] = -length*factor*pca.components_[0][1]
    else:
      angles[int(shoot_num)] = length*factor*pca.components_[0][1]

    if int(shoot_num) == 4:
      compensate()
  else:
    # angle = str(angles[1]) + " " + str(angles[2]) + " " + str(angles[3]) + " " + str(angles[4]) + " " + str((angles[2]+angles[4])/2) + " " + str((angles[1]+angles[3])/2)
    angle = str((angles[2]+angles[4])/2) + " " + str((angles[1]+angles[3])/2)

  if post_view_image_size == 'Original':
    if int(shoot_num) < 5:
      img = img.crop((2450, 600, 3550, 2900))
    else:
      img = img.crop((2450, 600, 3550, 2900))
  elif post_view_image_size == '2M':
    if int(shoot_num) < 5:
      img = img.crop((800, 210, 1150, 860))
    else:
      img = img.crop((800, 210, 1150, 860))
  
  img.save('static/fixture/' + filename)

  socketio.emit('image_ready',
                {'lot_number': lot_number,
                 'code': code,
                 'serial': serial,
                 'shoot_num': shoot_num,
                 'image_url' : filename,
                 'angle' : angle},
                namespace='/inspect')

@app.route('/shoot_<shoot_num>')
@nocache
def Shoot(shoot_num=None):
  global lot_number, code, serial
  lot_number = request.args.get("lot_number")
  code = request.args.get("code")
  serial = request.args.get("serial")

  path = Path.cwd() / 'static/fixture'
  
  if not path.exists():
    os.system('mkdir -p ' + str(path))

  if int(shoot_num) == 1:
    os.system('python3 pixel.py on 1')

    camera.setTouchAFPosition([50.0, 50.0])
    socketio.sleep(1)

  filename = str(lot_number) + '_' + str(code) + '_' + str(serial) + '_' + shoot_num.zfill(3) + '.jpg'

  res = camera.actTakePicture()
  if 'error' in res:
    camera_init()
    socketio.sleep(1)
    res = camera.actTakePicture()

  image_url = res['result'][0][0].replace('\/', '/')

  threads[int(shoot_num)] = socketio.start_background_task(target=load_image,
                                                           image_url=image_url,
                                                           filename=filename,
                                                           lot_number=lot_number,
                                                           code=code,
                                                           serial=serial,
                                                           shoot_num=shoot_num)
  # processes[int(shoot_num)] = Process(target=load_image, args=(image_url, filename, lot_number, code, serial, shoot_num, ))
  # processes[int(shoot_num)].start()

  # if int(shoot_num) == 5:
  #   for i in range(1, 6):
  #     processes[i].join()
  if int(shoot_num) == 5:
    os.system('python3 pixel.py off')

  return render_template('index.html')

@app.route('/ng')
@nocache
def ng():
  global lot_number, code, serial, ng_val

  lot_number = request.args.get("lot_number")
  code = request.args.get("code")
  serial = request.args.get("serial")
  ng_val = request.args.get("ng")

  socketio.emit('ng', namespace='/inspect')

  return render_template('index.html')

@app.route('/ledon', methods=['GET', 'POST'])
def ledon():
  os.system('python3 pixel.py on')
  return redirect(url_for('index'))

@app.route('/ledoff', methods=['GET', 'POST'])
def ledoff():
  os.system('python3 pixel.py off')
  return redirect(url_for('index'))

@app.route("/plason", methods=['GET', 'POST'])
def plason():
  GPIO.output(plasma_pin, 1)
  return redirect(url_for('index'))

@app.route("/plasoff", methods=['GET', 'POST'])
def plasoff():
  GPIO.output(plasma_pin, 0)
  return redirect(url_for('index'))

@app.route("/size_original", methods=['GET', 'POST'])
def size_original():
  post_view_image_size = 'Original'
  camera.setPostviewImageSize(post_view_image_size)
  return redirect(url_for('index'))

@app.route("/size_2m", methods=['GET', 'POST'])
def size_2M():
  post_view_image_size = '2M'
  camera.setPostviewImageSize(post_view_image_size)
  return redirect(url_for('index'))

@app.route('/video_feed')
def video_feed():
  return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen():
  global app
  app.get_frame_handle = liveview()

  while True:
    if app.get_frame_handle is not None:
      frame = app.get_frame_handle()
      yield (b'--frame\r\n'
             b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def liveview():
    mode = camera.getAvailableApiList()

    # some cameras need `startRecMode` before we can use liveview
    #   For those camera which doesn't require this, just comment out the following 2 lines
    if 'startRecMode' in (mode['result'])[0]:
        camera.startRecMode()
        time.sleep(2)

    camera.setLiveviewSize('L')
    sizes = camera.getLiveviewSize()
    print('Supported liveview size:', sizes)
    # url = camera.liveview("M")
    # url = camera.liveview()
    url = camera.startLiveviewWithSize('L')['result'][0].replace('\\', '')
    print(url)

    lst = pysony.SonyAPI.LiveviewStreamThread(url)
    lst.start()
    print('[i] LiveviewStreamThread started.')
    return lst.get_latest_view

if __name__ == '__main__':
  os.system('python3 pixel.py ceremony 0.3')
  camera_init()
  socketio.run(app, host=HOST, port=PORT)

