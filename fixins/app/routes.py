from flask import render_template, url_for, request, redirect
from app import app
from app.forms import ShootForm
from app.fixinsctrl import FixtureInspectorController

from pathlib import Path
import os, time, sys

from flask import make_response
from functools import wraps, update_wrapper
from datetime import datetime

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

@app.route('/')
@app.route('/index')
@nocache
def index():
    print(os.getcwd())
    p = Path('/dev/')
    usb_list = [usb.name for usb in p.glob('sd*[0-9]')]
    usb_list.insert(0, None)

    form = ShootForm()
    form.usb_drive.choices = usb_list

    p_mount = Path.cwd() / 'app/static'
    os.system('umount ' + str(p_mount))

    if len(os.listdir(os.getcwd() + '/app/static')) > 0:
        os.system('rm -r ' + os.getcwd() + '/app/static/*')

    return render_template('index.html', form=form)

@app.route('/shoot', methods=['GET', 'POST'])
@nocache
def Shoot():
    if request.method == "POST":
        req = request.form

        json = {"lot_number":req.get("lot_number"),
                "usb_drive":req.get("usb_drive")}

        p_mount = Path.cwd() / 'app/static'
        
        # print(req.get("usb_drive"), file=sys.stderr)
        if req.get("usb_drive") != 'None':
            os.system('umount ' + str(p_mount))
            os.system('mount /dev/' + req.get("usb_drive") + ' ' + str(p_mount))
        
        p_path = Path('fixture/' + req.get("lot_number"))
        path = p_mount/p_path
        
        if not path.exists():
            os.system('mkdir -p ' + str(path))
        
        os.system('python3 pixel.py on 1')        
        fictrl = FixtureInspectorController()
        fictrl.camera.setTouchAFPosition([50.0, 50.0])
        time.sleep(0.5)

        for j in range(4):
            fictrl.TakePicture(str(path) + '/' + req.get("lot_number") + '_' + str(j*90).zfill(3) + '.jpg')
            json.update({'image'+str(j*90).zfill(3):
                        str(p_path) + '/' + req.get("lot_number") + '_' + str(j*90).zfill(3) + '.jpg'})
            fictrl.Stepmotor(-100)

        fictrl.Stepmotor_idle()
        
        os.system('python3 pixel.py off')
            
        return render_template('shoot.html', title=req.get("lot_number"), json=json)