#! /bin/sh
cp ./docker-compose-app.service /etc/systemd/system/
systemctl enable docker-compose-app

cp ./81-thumbdrive.rules /etc/udev/rules.d/
sudo /etc/init.d/udev restart
chmod +x ./usb_restart.sh