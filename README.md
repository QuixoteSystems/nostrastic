
![nostrastic-alargado](https://github.com/QuixoteSystems/nostrastic/assets/82296005/e913b878-4319-4e4a-873c-5779752ebf3b)

**Bridge to publish Nostr posts and send/receive DMs over LoRa using a Meshtastic device.**

Note: This is a Beta version (Proof of Concept), so I am still debugging and improving the code. PRs are welcomed.


# First steps

### To use Nostrastic you need at least:
- One Meshtastic Device
- One Meshtastic Gateway Device, this means a Meshtastic Device with internet connection and MQTT enable.
- Running Nostrastic with a computer/server with internet connection

### Configure your Meshtastic devices
First of all you have to set up certains options in your Meshtastic Device and in your Meshtastic Gateway.
- In your Meshtastic Device (with no internet):
  
  * Add mqtt channel as secondary (*IMPORTANT: name has to be mqtt in lower case*)

- In your Meshtastic Gateway Device (with internet):
  
  * Add mqtt channel as secondary (*IMPORTANT: name has to be mqtt in lower case*)
  * In MQTT Config:
    * Enable MQTT
    * Enable JSON output
    * Disable Encryption

# Start using Nostrastic
1- Clone or Download this repo.

2- Install packages requirements:
```shell
pip install -r requirements.txt
```

3- Fill up with your own data *.env* file
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

4- Fill up with your Nostr contacts *contacts.json* file:
```json
{
    "(nickname_1)":"npub...",
    "(nickname_2)":"npub...",
    "(nickname_3)": "npub..."
}
```

5- Run main.php
```shell
python3 main.py
```
6- Automatically it will create *nostrastic.log* where you can see what is happening

7- From your Meshtastic device:
  - You have to go to mqtt channel and write: (post) or (nickname) following the post text or DM message:
    * To send a Nostr post:
      
      ```(post) This is an amazing note for all nostriches. ``` *--> This will send that text like a post to your Nostr account.*
        
    * To send a DM to your contact (remember this nickname has to be on contacts.json):

      ```(nickname_1) Hi Pleb! How are you doing?``` *--> This will send that text like a DM to your contact.*

#### If you like this project, you can help by sending me some sats:

  ![quixote LN wallet](https://github.com/QuixoteSystems/nostrastic/assets/82296005/709cc5d3-0e99-4e6c-80f2-8d5ddec290f2)

  LN address: quixote@getalby.com
