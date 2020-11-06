1. install git
```
sudo apt-get install git
```
2. install docker
```
sudo apt-get install apt-transport-https ca-certificates software-properties-common gnupg-agent -y
curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh
sudo 
```

3. build and run docker-compose
```
docker-compose build --force-rm
docker-compose run -d
```

4. run ./setup/setup.sh
```
run ./setup/setup.sh
```