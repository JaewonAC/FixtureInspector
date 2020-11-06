1. install git
```
sudo apt-get install git
```
2. install docker and docker-compose
https://dev.to/rohansawant/installing-docker-and-docker-compose-on-the-raspberry-pi-in-5-simple-steps-3mgl
```
curl -fsSL get.docker.com | sh
sudo usermod -aG docker pi
sudo reboot
docker run hello-world
sudo apt-get install -y libffi-dev libssl-dev
sudo apt-get install -y python3 python3-pip
sudo apt-get remove python-configparser
sudo pip3 -v install docker-compose
```

3. wifi connect to sony camera
```
sudo raspi-config 
```
or
```
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```
write
```
network={
  ssid=
  psk=
}
```

4. build and run docker-compose
```
fixtureinspector/docker-compose build --force-rm
fixtureinspector/docker-compose run -d
```

5. run ./setup/setup.sh
```
run ./setup/setup.sh
```