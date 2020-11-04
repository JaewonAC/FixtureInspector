import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

control_pins = [22, 24, 23, 25]

for pin in control_pins:
  GPIO.setup(pin, GPIO.OUT)
  GPIO.output(pin, 0)

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

# for i in range(512):
#   for halfstep in range(8):
#     for pin in range(4):
#       GPIO.output(control_pins[pin], halfstep_seq[halfstep][pin])
#     time.sleep(0.001)

halfstep = 0
for i in range(12):
  for j in range(100):
    for pin in range(4):
      GPIO.output(control_pins[pin], halfstep_seq[halfstep][pin])
    halfstep += 1
    if halfstep == 8:
      halfstep = 0
    elif halfstep == -1:
      halfstep = 7
    print(halfstep)
    time.sleep(0.001)
  time.sleep(0.5)

GPIO.cleanup()