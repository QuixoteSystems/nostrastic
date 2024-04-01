#!/usr/bin/env python
''' MQTT Client to get and send payload to a specific topic on a MQTT Server '''

import os
import json
import time
import paho.mqtt.client as mqtt
from paho.mqtt.subscribeoptions import SubscribeOptions
import tornado.ioloop

from pynostr.message_pool import MessagePool
from pynostr.base_relay import RelayPolicy
from pynostr.relay import Relay

from dotenv import load_dotenv
from nostrastic.enviroment import set_text, get_text, set_gateway_dec, set_gateway_hex, \
    get_gateway_hex, write_info_log, write_error_log
from nostrastic.nostr_messenger import NostrMessenger

# take environment variables from .env
load_dotenv()

class MqttClient:
    def __init__(self):
        self.mqtt_srv = os.environ.get('MQTT_SRV')
        self.mqtt_port = int(os.environ.get('MQTT_PORT'))
        self.mqtt_user = os.environ.get('MQTT_USER')
        self.mqtt_pass = os.environ.get('MQTT_PASS')
        self.subscription = os.environ.get('SUSCRIPTION')
        self.publishing = os.environ.get('PUBLISHING')
        self.mesh_device = os.environ.get('MESH_DEVICE')
        self.mesh_gw_hex = os.environ.get('MESH_GW_HEX')
        self.relay = os.environ.get('RELAY')
        
        
    def mqtt_connection(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.username_pw_set(self.mqtt_user, self.mqtt_pass)  # user and password for MQTT Meshtastic Server
        client.connect(self.mqtt_srv, self.mqtt_port, 120)  # Server connection
        return client


    def on_connect(self, client, userdata, flags, rc):
        '''
        The callback for when the client receives a CONNACK response from the server.
        Subscribing in on_connect() means that if we lose the connection and reconnect 
        then subscriptions will be renewed.
        '''
        if rc == 0:
            write_info_log(f"Connection to MQTT Server: {self.mqtt_srv}: Successful.")
        else:
            write_info_log(f"Connection to MQTT Server: {self.mqtt_srv}: Error: {str(rc)}")

        # With this option we unsubscribe to our own message to avoid resending old messages
        options = SubscribeOptions(qos=1, noLocal=True)
        # It has to be actived JSON on the device and then is not encrypted
        client.subscribe(self.subscription, options=options)
        write_info_log(f'MQTT Subscribed to: {self.subscription}')



    def on_message(self, client, userdata, msg):
        ''''
        The callback for when a PUBLISH message is received from the server.
        Send from MQTT Server to Nostr Relays
        '''
        nostr_messenger = NostrMessenger()
        payload = json.loads(msg.payload)
        try:
            decimal_node_id = payload["from"]
            hex_node_id = hex(decimal_node_id).lstrip("0x")
        
            mqtt_gateway_hex = payload["sender"]
            # Removing first character
            mqtt_gateway_hex = mqtt_gateway_hex[1:]
            set_gateway_hex(mqtt_gateway_hex)
            # Convert to Decimal
            mqtt_gateway_dec = int(mqtt_gateway_hex, 16)
            set_gateway_dec(mqtt_gateway_dec)
            time.sleep(1)

        except KeyError as error:
            # It need to wait 1 sec to format to meshtastic JSON allowed payload
            time.sleep(1)
            #pass
    
        try:
            if hex_node_id == self.mesh_device:
                old_text = get_text()
                text = payload["payload"]["text"]

                if old_text != text:
                    set_text(text)
                    nostr_messenger.publish()
                    time.sleep(1)
                
                else:
                    return True

        except KeyError as error:
            write_error_log(f"JSON Payload Error: {error}")

        except Exception as error:
            write_error_log(f'Exception in on_message: {error}')
        '''
        except TypeError:
            if hex_node_id == self.mesh_device:
                old_text = get_text()
                text = payload["payload"]

                if old_text != text:
                    set_text(text)

                    if hex_node_id == self.mesh_device:
                        nostr_messenger.publish()
                        time.sleep(1)
        '''
        


    def mqtt_publish(self, client, text):
        '''
        Here is the Meshtastic Gateway Node with his Topic Path
        '''
        topic = self.publishing + get_gateway_hex()
        result = client.publish(topic, text)
        # Allowing time to send and receive the reply
        #time.sleep(2)
        status = result[0]

        for _ in range(3):
            if status == 0:
                write_info_log(f"Send to topic: {topic}")
                write_info_log(f'Data published: {text}')
                break

            else:
                write_error_log(f"Failed to send message to topic {topic}")
                #time.sleep(2)
                if status == 4:
                    write_error_log(f'MQTT Gateway wrong. Error: {status}. Connection Refused.')
                else:
                    write_error_log(f'Error MQTT Client: {status}')
                    # Allowing time to send and receive the reply
                    #time.sleep(2)
                    result = client.publish(topic, text)
                    status = result[0]
                



    def listener(self):
        '''
        Listener of a channel in a MQTT Server to get user events.
        '''
        client = self.mqtt_connection()
        while True:
            # Receive events from relays Library Pynostr
            io_loop = tornado.ioloop.IOLoop.current()
            message_pool = MessagePool(first_response_only=False)
            policy = RelayPolicy()
            Relay(
                self.relay,
                message_pool,
                io_loop,
                policy,
                timeout=3,
                close_on_eose=False,
                message_callback=client.loop()
            )
