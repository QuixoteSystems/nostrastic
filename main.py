#!/usr/bin/python3
''' Main '''

import os
import sys
import threading

from dotenv import load_dotenv
import pyfiglet

from nostrastic.mqtt_client import MqttClient
from nostrastic.nostr_messenger import NostrMessenger
from nostrastic.enviroment import init_text, init_nostr_text, init_log, end_log

# take environment variables from .env
load_dotenv()

# Nostrastic Purple Header
nostrastic = pyfiglet.figlet_format(" Nostrastic")
print(("\033[95m" + nostrastic))
print("\033[1;32m" + '                 version 0.0.1\n')
print('\033[96m' + 'Dev: Quixote (https://github.com/QuixoteSystems)\n')
print('\033[0;93m' + '      ⚡ Zaps to: quixote@getalby.com\n')
# Back to white
print('\033[00m')

# initialize texts
init_text()
init_nostr_text()

# Device to send post and send/receive DMs (Meshtastic Gateway)
MESH_DEVICE = os.environ.get('MESH_DEVICE')

print(f'Listening for Meshtastic Device: {MESH_DEVICE}\n')


if __name__ == "__main__":

    init_log()

    # Initialize Class instance
    mqtt_client = MqttClient()
    nostr_messenger = NostrMessenger()

    try:
        p1 = threading.Thread(target=mqtt_client.listener, args=())
        p2 = threading.Thread(target=nostr_messenger.listener, args=())

        p1.start()
        p2.start()

        p1.join()
        p2.join()

    except KeyboardInterrupt as stop:
        print('Finishing Nostrastic...\n')
        end_log()
        sys.exit()

