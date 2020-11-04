import sys, board, neopixel, time

pixel_pin = board.D18
pixels = None
num_pixels = 10

if __name__ == '__main__':
  intensity = 1
  if len(sys.argv) > 2:
    intensity = float(sys.argv[2])

  pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=intensity, auto_write=True, pixel_order=neopixel.RGBW)

  if sys.argv[1] == 'on':
    pixels.fill((255, 255, 255, 255))
  elif sys.argv[1] == 'off':
    pixels.fill((0, 0, 0, 0))
  elif sys.argv[1] == 'red':
    pixels.fill((0, 255, 0, 0))
  elif sys.argv[1] == 'green':
    pixels.fill((255, 0, 0, 0))
  elif sys.argv[1] == 'blue':
    pixels.fill((0, 0, 255, 0))
  elif sys.argv[1] == 'ceremony':
    pixels.fill((0, 255, 0, 0))
    time.sleep(0.3)
    pixels.fill((255, 0, 0, 0))
    time.sleep(0.3)
    pixels.fill((0, 0, 255, 0))
    time.sleep(0.3)
    pixels.fill((0, 0, 0, 255))
    time.sleep(0.3)
    pixels.fill((255, 255, 255, 255))
    time.sleep(0.3)

    for j in range(255):
      for i in range(num_pixels):
        pixel_index = ((i * 256 // num_pixels) + j) & 255

        if pixel_index < 0 or pixel_index > 255:
          r = g = b = 0
        elif pixel_index < 85:
          r = int(pixel_index * 3)
          g = int(255 - pixel_index * 3)
          b = 0
        elif pixel_index < 170:
          pixel_index -= 85
          r = int(255 - pixel_index * 3)
          g = 0
          b = int(pixel_index * 3)
        else:
          pixel_index -= 170
          r = 0
          g = int(pixel_index * 3)
          b = int(255 - pixel_index * 3)

        pixels[i] = (r, g, b, 0)
      time.sleep(0.001)

    pixels.fill((0, 0, 0, 0))
