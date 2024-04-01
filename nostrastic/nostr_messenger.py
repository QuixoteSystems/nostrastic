#!/usr/bin/env python
'''Nostr Messenger to send and receive DMs over Meshtastic.'''

import os
import uuid
import ssl
import time
import json
import threading
from binascii import unhexlify
import tornado.ioloop
from tornado import gen

import nostr.event
import nostr.key
from nostr.relay_manager import RelayManager

from pynostr.base_relay import RelayPolicy
from pynostr.encrypted_dm import EncryptedDirectMessage
from pynostr.event import Event, EventKind
from pynostr.filters import Filters, FiltersList
from pynostr.key import PrivateKey, PublicKey
from pynostr.message_pool import MessagePool
from pynostr.message_type import RelayMessageType
from pynostr.relay import Relay
from pynostr.utils import get_public_key, get_timestamp

from dotenv import load_dotenv
from nostrastic.enviroment import get_text, get_gateway_dec, get_nostr_text, set_nostr_text, \
    write_info_log, write_error_log


class NostrMessenger:
    '''
    Class to manage the Nostr DMs between a Nostr user with a Nostr App and 
    Nostr user with Meshtastic Device
    '''
    def __init__(self):
        load_dotenv()
        self.relay = os.environ.get('RELAY')
        self.nsec = os.environ.get('NSEC')
        self.hex_npub = os.environ.get('HEX_NPUB')


    def receive_dm(self, message_json):
        '''
        Receive DM from Nostr and sent to a MQTT Channel and then to Meshtastic
        '''
        sender_pk = PrivateKey() if len(self.nsec) == 0 else PrivateKey.from_nsec(self.nsec)
        message_type, *payload = message_json

        if message_type == RelayMessageType.EVENT:
            event = Event.from_dict(payload[1])
            # Getting the Event Pub Key
            event_pubkey = payload[1]['pubkey']
            pubkey_hex = PublicKey(unhexlify(event_pubkey))
            # Casting to Bech32 format to allow receive DMs from this Nostr user
            npub = pubkey_hex.bech32()

            if event.kind == EventKind.ENCRYPTED_DIRECT_MESSAGE and event.has_pubkey_ref(sender_pk.public_key.hex()):
                encrypted_dm = EncryptedDirectMessage.from_event(event)
                recipient = get_public_key(npub)

                if recipient:
                    sender_bech32 = recipient.bech32()
                    try:
                        write_info_log(f"You received a DM from: {sender_bech32}")
                        encrypted_dm.decrypt(sender_pk.hex(), public_key_hex=recipient.hex())
                        nostr_old_text = get_nostr_text()
                        nostr_new_text = encrypted_dm.cleartext_content

                        if nostr_old_text != nostr_new_text:
                            set_nostr_text(nostr_new_text)
                            # Checking if the sender is in the contact list
                            # Reading file with your Nostr contacts
                            with open('contacts.json', encoding="utf-8") as contacts_file:
                                contacts = contacts_file.read()
                            # Casting string to JSON Dict
                            dicto = json.loads(contacts)
                            user = sender_bech32[:5] + '...' + sender_bech32[-5:]
                            # Searching the name of the user
                            for key, value in dicto.items():
                                if value == sender_bech32:
                                    user = key
                                    break
                            from nostrastic.mqtt_client import MqttClient
                            mqtt_client = MqttClient()
                            client = mqtt_client.mqtt_connection()
                            #write_info_log(f'Connected to MQTT Server: {client.is_connected()}')

                            if client.is_connected():
                                # Adding time to connect properly to MQTT Server
                                client.loop_start()
                                mqtt_text = '{"channel":2,"from":' + get_gateway_dec() +',"type":"sendtext","payload":"' \
                                    + user + ' ' + encrypted_dm.cleartext_content + '"}'
                            else:
                                client = mqtt_client.mqtt_connection()
                                # Adding time to connect properly to MQTT Server
                                client.loop_start()
                                mqtt_text = '{"channel":2,"from":' + get_gateway_dec() +',"type":"sendtext","payload":"' \
                                    + user + ' ' + encrypted_dm.cleartext_content + '"}'

                    except Exception as error:
                        write_error_log(f'Error Nostr Messenger: {error}')

                    try:
                        client.loop()
                    except AttributeError:
                        write_error_log('MQTT Publish: Trying again...')
                        #time.sleep(1)
                        client.loop(1)

                    mqtt_client.mqtt_publish(client, mqtt_text)
                    

                else:
                    raise Exception("Receiver not valid")

        elif message_type in (RelayMessageType.OK, RelayMessageType.NOTICE):
            write_info_log(f'Nostr Note Result: {message_json}')



    def send_dm(self, receiver, message):
        '''
        Send a DM from Nostr to Meshtastic
        '''
        sender_pk = PrivateKey() if len(self.nsec) == 0 else PrivateKey.from_nsec(self.nsec)
        write_info_log(f"You sent a DM with your PubKey: {sender_pk.public_key.bech32()}")

        recipient = get_public_key(receiver)

        if recipient != "":
            #print(f"Sending DM to {recipient.bech32()}\n")
            write_info_log(f"DM Sent to :{recipient.bech32()}")
        else:
            raise Exception("Receiver not valid")

        dm = EncryptedDirectMessage()
        dm.encrypt(
            sender_pk.hex(),
            cleartext_content=message,
            recipient_pubkey=recipient.hex(),
        )

        filters = FiltersList(
            [
                Filters(
                    authors=[recipient.hex()],
                    kinds=[EventKind.ENCRYPTED_DIRECT_MESSAGE],
                    since=get_timestamp(),
                    limit=10,
                )
            ]
        )

        subscription_id = uuid.uuid1().hex
        io_loop = tornado.ioloop.IOLoop.current()
        message_pool = MessagePool(first_response_only=True)
        policy = RelayPolicy()
        r = Relay(
            self.relay,
            message_pool,
            io_loop,
            policy,
            timeout=5,
            close_on_eose=False,
            message_callback=self.receive_dm,
        )

        dm_event = dm.to_event()
        dm_event.sign(sender_pk.hex())
        r.publish(dm_event.to_message())
        r.add_subscription(subscription_id, filters)

        def connect_and_listen():
            try:
                result = io_loop.run_sync(r.connect)
                return result
            except gen.Return:
                pass

        # Inicialize connection and start listening secondary thread
        connection_thread = threading.Thread(target=connect_and_listen)
        connection_thread.start()
        connection_thread.join()
        r.close()
    

    def publish(self):
        '''
        Function to publish on Nostr a Post or DM if has a prefix with username
        '''
        # Publish to a Relay
        nostr_messenger = NostrMessenger()
        relay_manager = RelayManager()
        relay_manager.add_relay(self.relay)
        relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE}) # NOTE: This disables ssl certificate verification
        time.sleep(1.25) # allow the connections to open

        # Importing Enviroment Variables
        private_key = nostr.key.PrivateKey.from_nsec(self.nsec)
        texto = get_text()

        # Reading file with your Nostr contacts
        with open('contacts.json', encoding="utf-8") as contacts_file:
            contacts = contacts_file.read()
        # Casting string to JSON Dict
        dicto = json.loads(contacts)

        # Iterating the Dict with user contacts to check if is there
        for key, value in dicto.items():
            if texto.startswith(key):
                # Deleting the nickname for the DM chat
                texto =texto.replace(key, "")
                # Call to send DM
                nostr_messenger.send_dm(value, texto)
                write_info_log('DM sent to Nostr.')
                relay_manager.close_connections()

            elif texto.startswith('(post)'):
                write_info_log(f'Text to Publish on Nostr: {texto}')
                # Deleting the string '(post)' for the Nostr Post
                texto =texto.replace('(post)', "")
                texto = texto + ' _Posted by #Nostrastic'
                event = nostr.event.Event(public_key=self.hex_npub, content=texto)
                private_key.sign_event(event)
                relay_manager.publish_event(event)
                time.sleep(1) # allow the messages to send
                write_info_log('DM sent to Nostr.')
                relay_manager.close_connections()




    def listener(self):
        '''
        Listener to get DMs from Nostr Relays to send to a MQTT Server and then to Meshtastic Device
        '''
        while True:
            message_pool = MessagePool(first_response_only=True)
            policy = RelayPolicy()
            Relay(
                self.relay,
                message_pool,
                policy,
                timeout=3,
                close_on_eose=True,
                message_callback=self.receive_dm)
