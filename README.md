# Sensors data over multicast

## Building packages

```bash  
apt-get -y install dh-make
./build-debian-packages.sh
ls debs/
```  

## Installation 

### receiver

```bash  
apt-get -y install python3 python3-configargparse
dpkg -i debs/sensors-receiver_0.0.1_all.deb
```  

### sender
```bash  
apt-get -y install python3 python3-configargparse lm-sensors
dpkg -i debs/sensors-sender_0.0.1_all.deb
```  

##  Usage

### receiver
```bash  
systemctl enable sensors-receiver.service
systemctl start sensors-receiver.service
tail -f -n 20 /var/opt/sensors.log
```  

### sender
```bash  
systemctl enable sensors-sender.service
systemctl start sensors-sender.service
```  
