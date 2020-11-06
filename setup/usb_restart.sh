#! /bin/sh

python3 /home/pi/fixtureinspector/fixins/pixel.py red 0.3
/usr/local/bin/docker-compose -f /home/pi/fixtureinspector/docker-compose.yml restart

