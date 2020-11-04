import sys
from pathlib import Path

# p = Path('/dev/')
# usb_list = [usb.name for usb in p.glob('sd*[0-9]')]
# for usb in usb_list:
#   print(usb)


if __name__ == '__main__':
  print(len(sys.argv))
  print(sys.argv[1])
  print(float(sys.argv[2])+2)