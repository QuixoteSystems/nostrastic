
![nostrastic-alargado](https://github.com/QuixoteSystems/nostrastic/assets/82296005/e913b878-4319-4e4a-873c-5779752ebf3b)

Bridge to publish Nostr posts and send/receive DMs over LoRa using a Meshtastic device.

Note: This is a first Beta version and I am still debugging and improving the code. PRs are welcomed.


# First steps

### To use Nostrastic you need at least:
- One Meshtastic Device
- One Meshtastic Gateway Device, this means a Meshtastic Device with internet connection and MQTT enable.
- Running Nostrastic with a computer/server with internet connection

### Configure your Meshtastic devices
First of all you have to set up certains options in your Meshtastic Device and in your Meshtastic Gateway.
- In your Meshtastic Device (with no internet):
  
  * Add mqtt channel as secondary (IMPORTANT: name has to be mqtt in lower case)

- In your Meshtastic Gateway Device (with internet):
  
  * Add mqtt channel as secondary (IMPORTANT: name has to be mqtt in lower case)
  * In MQTT Config:
    * Enable MQTT
    * Enable JSON output
    * Disable Encryption

# Start using Nostrastic
1- Clone or Download this repo.

2- Fill up with your own data .env file
```python
## NOSTR ###################################################################
# Your Public Keys
NPUB = 'npub...'
HEX_NPUB = 'hexadecimal...'

# Your Private Keys
NSEC = 'nsec...'
HEX_NSEC = 'hexadecimal'

# Relays
# Relay where senders and receivers users have to be
RELAY = 'wss://YOUR_RELAY'

## MQTT ####################################################################
# Meshtastic MQTT Server (Default) you can change for your own MQTT server
MQTT_SRV = 'mqtt.meshtastic.org'
MQTT_PORT = 1883
MQTT_USER = DEFAULT_USER
MQTT_PASS = DEFAULT_PASSWORD
# Suscription to mqtt JSON Channel has to be this path: json/mqtt other doesnt work
SUSCRIPTION = 'msh/YOUR/PATH/json/mqtt/#'
# Channel from MQTT where message are published
PUBLISHING = 'msh/YOUR/PATH/json/mqtt/!'

## MESHTASTIC ###############################################################
# Your Meshtastic ID Device from where you are writing over LoRa (without ! symbol)
# If change the MESH_DEVICE needs to reload the enviroment variables (close and open folder VS)
MESH_DEVICE = '12345678'
```

3- Install packages requirements:
```shell
pip install -r requirements.txt
```
4- Run main.php
```shell
python3 main.py
```
5- Automatically it will create nostrastic.log where you can see what is happening
