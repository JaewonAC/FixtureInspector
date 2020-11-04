FROM python:3.8-buster

RUN apt-get update && apt-get upgrade -y
RUN apt-get install python3-pip -y
RUN python3 -m pip install git+https://github.com/JaewonAC/sony_camera_api.git
RUN pip3 install --no-cache-dir -r requirements.txt
RUN python3 -m pip install --force-reinstall adafruit-blinka

RUN mkdir /fixins
WORKDIR /fixins
EXPOSE 5000