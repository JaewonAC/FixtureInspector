from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, request, redirect, make_response
from threading import Thread, Event
import os, time
from pathlib import Path

from functools import wraps, update_wrapper
from datetime import datetime

from forms import ShootForm
from fixinsctrl import FixtureInspectorController

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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'brf89hy2349hg8f9r8239hjugv0amz'
app.config['DEBUG'] = False

#turn the flask app into a socketio app
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()

fictrl = FixtureInspectorController()

@app.route('/')
@app.route('/index')
@nocache
def index():
    p = Path('/dev/')
    usb_list = [usb.name for usb in p.glob('sd*[0-9]')]
    usb_list.insert(0, None)

    form = ShootForm()
    form.usb_drive.choices = usb_list

    path_mount = Path.cwd() / 'static/fixture'
    os.system('umount ' + str(path_mount))

    if len(os.listdir(os.getcwd() + '/static/fixture')) > 0:
        os.system('rm -r ' + os.getcwd() + '/static/fixture/*')

    return render_template('index.html', form=form)

@app.route('/shoot', methods=['GET', 'POST'])
@nocache
def Shoot():
  if request.method == "POST":
    req = request.form

    json = {"lot_number":req.get("lot_number"),
            "usb_drive":req.get("usb_drive")}

    path_mount = Path.cwd() / 'static/fixture'
    
    # print(req.get("usb_drive"), file=sys.stderr)
    if req.get("usb_drive") != 'None':
      os.system('umount ' + str(path_mount))
      os.system('mount /dev/' + req.get("usb_drive") + ' ' + str(path_mount))
    
    path_sub = Path('fixture/' + req.get("lot_number"))
    path = path_mount/path_sub
    
    if not path.exists():
      os.system('mkdir -p ' + str(path))
    
    socketio.start_background_task(ShootThread, lot_number=req.get("lot_number"), path=path, path_sub=path_sub)
            
    return render_template('shoot.html', title=req.get("lot_number"), json=json)

def ShootThread(*args, **kwargs):
    global thread, fixctrl

    os.system('python3 pixel.py on 1')

    fictrl.camera.setTouchAFPosition([50.0, 50.0])
    socketio.sleep(0.5)
  
    for j in range(4):
      fictrl.TakePicture(str(kwargs['path']) + '/' + kwargs['lot_number'] + '_' + str(j*90).zfill(3) + '.jpg')
      fictrl.Stepmotor(-100)
      socketio.emit('image_ready',
                    {'image_url' : str(kwargs['path_sub']) + '/' + kwargs['lot_number'] + '_' + str(j*90).zfill(3) + '.jpg'},
                    namespace='/test')
    
    fictrl.Stepmotor_idle()
    
    os.system('python3 pixel.py off')

@app.route('/on', methods=['GET', 'POST'])
def on():
    os.system('python3 pixel.py on')
    return redirect(url_for('index'))

@app.route('/off', methods=['GET', 'POST'])
def off():
    os.system('python3 pixel.py off')
    return redirect(url_for('index'))

@app.route('/idle', methods=['GET', 'POST'])
def idle():
    fictrl = FixtureInspectorController()
    fictrl.Stepmotor_idle()
    return redirect(url_for('index'))

if __name__ == '__main__':
  os.system('python3 pixel.py ceremony 0.3')
  socketio.run(app, host="0.0.0.0", port=5000)

