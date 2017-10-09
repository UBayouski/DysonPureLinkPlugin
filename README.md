# Dyson Pure Link Devices Plugin

Our homes get more and more smart devices connected to the Internet. Some of us have different air purifier devices because the air quality especially in big cities leaves much to be desired. 

There are many options for purifier devices and one of them is Dyson.

You can read its sensors data and use it with other smart devices, personal projects like smart home or just for fun and to get some practical experience.

To connect to Dyson Link device, we use MQTT protocol and Python 2.7 code. If you need it in Python 3 you can easily migrate to it by changing import of Queue module to lowercase queue.

### Getting sensors readings:
#### python run_plugin.py

### Change Fan mode:
#### python run_plugin.py –fan FAN|OFF|AUTO

### Change standby mode: 
#### python run_plugin.py –standby ON|OFF
