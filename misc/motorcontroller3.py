import RPi.GPIO as GPIO
import time, multiprocessing
from datetime import timedelta
from multiprocessing import Process, Event

class MotorController(multiprocessing.Process):
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
  d_gain = 0.001
  i_gain = 0.001

  stability = 0

  start_time = 0

  interval = 0.01

  maximum_power = 100

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

  def __init__(self, target_step, sleep=0):
    super(MotorController, self).__init__()
    self.finished = multiprocessing.Event()
    self.target_step = target_step
    self.sleep = sleep
  
  def cancel(self):
    """Stop the timer if it hasn't finished yet"""
    self.finished.set()

  def run(self):
    time.sleep(self.sleep)
    self.finished.wait(self.interval)
    
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

    while self.stability < 10 and not self.finished.is_set():
      current_time = time.time()
      time_delta = current_time - self.last_time
      
      if(time_delta > self.interval):
        error = self.target_step - self.step
        speed = (self.step - self.last_step)/time_delta
    
        control = self.p_gain*error + self.i_gain*error*time_delta + self.d_gain*(error - self.last_error)/time_delta

        if error ==0 and speed == 0:
          self.pwm_a.ChangeDutyCycle(0)
          self.pwm_b.ChangeDutyCycle(0)
          self.stability += 1
        else:
          if control > 0:
            self.pwm_a.ChangeDutyCycle(self.maximum_power if control > self.maximum_power else control)
            self.pwm_b.ChangeDutyCycle(0)
          else:
            self.pwm_a.ChangeDutyCycle(0)
            self.pwm_b.ChangeDutyCycle(self.maximum_power if -control > self.maximum_power else -control)
          
          self.stability = 0

        self.last_step = self.step
        self.last_error = error
        self.last_time = current_time

      time.sleep(0.001)
    self.finished.set()
    
    GPIO.remove_event_detect(self.encoder_pin_a)
    GPIO.remove_event_detect(self.encoder_pin_b)
    GPIO.cleanup()

if __name__ == "__main__":
  t = time.time()
  motorctrl = MotorController(1133)
  motorctrl.start()
  motorctrl.join()
  print('hi' + str(motorctrl.target_step))
  # for i in range(1):
    # motorctrl.rotate(1133)