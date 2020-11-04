#! /bin/sh

python3 /home/pi/fixins/fixins/pixel.py red 0.3
/usr/local/bin/docker-compose -f /home/pi/fixins/docker-compose.yml restart