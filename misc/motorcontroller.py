import RPi.GPIO as GPIO
import time, threading, signal
from datetime import timedelta

class ProgramKilled(Exception):
    pass
    
def signal_handler(signum, frame):
    raise ProgramKilled
    
class Job(threading.Thread):
  def __init__(self, interval, execute, *args, **kwargs):
    threading.Thread.__init__(self)
    self.daemon = False
    self.stopped = threading.Event()
    self.interval = interval
    self.execute = execute
    self.args = args
    self.kwargs = kwargs
      
  def stop(self):
    self.stopped.set()
    self.join()

  def run(self):
    while not self.stopped.wait(self.interval.total_seconds()):
      self.execute(*self.args, **self.kwargs)

class MotorController():
  encoder_pin_a = 27
  encoder_pin_b = 17
  pwm_a_pin = 15
  pwm_b_pin = 18

  pwm_a = None
  pwm_b = None

  target_step = 0

  step = 0
  last_step = 0

  error = 0
  last_error = 0

  p_gain = 1
  d_gain = 0.01
  i_gain = 0.01

  stablity = 0

  start_time = 0

  interval = 0.01

  maximum_power = 50

  def encoder_a_callback(self, channel):
    if GPIO.input(self.encoder_pin_a) == GPIO.input(self.encoder_pin_b):
      self.step -= 1
    else:
      self.step += 1
  
  def encoder_b_callback(self, channel):
    if GPIO.input(self.encoder_pin_a) == GPIO.input(self.encoder_pin_b):
      self.step += 1
    else:
      self.step -= 1

  def __init__(self):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self.encoder_pin_a, GPIO.IN)
    GPIO.setup(self.encoder_pin_b, GPIO.IN)
    GPIO.setup(self.pwm_a_pin, GPIO.OUT)
    GPIO.setup(self.pwm_b_pin, GPIO.OUT)

    self.pwm_a = GPIO.PWM(self.pwm_a_pin, 1000)
    self.pwm_a.start(0)

    self.pwm_b = GPIO.PWM(self.pwm_b_pin, 1000)
    self.pwm_b.start(0)

    GPIO.add_event_detect(self.encoder_pin_a, GPIO.BOTH, callback=self.encoder_a_callback)
    GPIO.add_event_detect(self.encoder_pin_b, GPIO.BOTH, callback=self.encoder_b_callback)

    self.start_time = time.time()
    self.last_time = time.time()

  def __del__(self):
    # self.pwm_a.ChangeDutyCycle(0)
    # self.pwm_b.ChangeDutyCycle(0)
    GPIO.remove_event_detect(self.encoder_pin_a)
    GPIO.remove_event_detect(self.encoder_pin_b)
    GPIO.cleanup()

  def loop(self):
    current_time = time.time()
    time_delta = current_time - self.last_time

    error = self.target_step - self.step
    speed = (self.step - self.last_step)/time_delta

    # p_control = self.p_gain*error
    # i_control = self.i_gain*error*time_delta
    # d_control = self.d_gain*(error - self.last_error)/time_delta
    # control = p_control + i_control + d_control
    
    control = self.p_gain*error + self.i_gain*error*time_delta + self.d_gain*(error - self.last_error)/time_delta

    self.last_time = current_time
    self.last_step = self.step
    self.last_error = error

    # print('step : ' + str(step) + ' last step :' + str(last_step))
    # print('speed : ' + str(speed))
    # print('target step : ' + str(self.target_step) + ' step : ' + str(self.step))
    # print('error : ' + str(error) + ' control : ' + str(control))
    # print("stability " + str(self.stability))
    # print('time_delta : ' + str(time_delta))
    # print('p : ' + str(p_control) + ' i : ' + str(i_control) + ' d : ' + str(d_control))

    if error ==0 and speed == 0:
      self.pwm_a.ChangeDutyCycle(100)
      self.pwm_b.ChangeDutyCycle(100)
      if self.stability > 10:
        print('end : ' + str(time.time() - self.start_time))
      else:
        self.stability += 1
        # threading.Timer(self.interval, self.loop).start()
    else:
      if control > 0:
        self.pwm_a.ChangeDutyCycle(self.maximum_power if control > self.maximum_power else control)
        self.pwm_b.ChangeDutyCycle(0)
        self.stability = 0
        # threading.Timer(self.interval, self.loop).start()
      else:
        self.pwm_a.ChangeDutyCycle(0)
        self.pwm_b.ChangeDutyCycle(self.maximum_power if -control > self.maximum_power else -control)
        self.stability = 0
        # threading.Timer(self.interval, self.loop).start()

  def rotate(self, target_step=99):
    self.stability = 0
    self.target_step += target_step
    # self.loop()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    job = Job(interval=timedelta(seconds=self.interval), execute=self.loop)
    job.start()

    while True:
      if self.stability > 10:
        print("target step reached")
        job.stop()
        break

      try:
        time.sleep(self.interval)
      except ProgramKilled:
        print("Program killed: running cleanup code")
        job.stop()
        break

if __name__ == "__main__":
  motorctrl = MotorController()
  
  for i in range(1):
    motorctrl.rotate(1133)