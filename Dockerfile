FROM soluto/python-flask-sklearn-docker-template
RUN mkdir /fixins
WORKDIR /fixins

RUN python3 -m pip install --no-cache-dir git+https://github.com/JaewonAC/sony_camera_api.git
RUN conda install Flask \
                  flask-wtf \
                  flask-socketio \
                  python-dotenv \
                  RPi.GPIO \
                  rpi_ws281x\
                  adafruit-circuitpython-neopixel\
                  Pillow \
                  numpy \
                  sklearn && \
    python3 -m pip install --no-cache-dir --force-reinstall adafruit-blinka

EXPOSE 5000