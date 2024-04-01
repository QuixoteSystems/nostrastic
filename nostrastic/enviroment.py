#!/usr/bin/python3
''' 
Enviroment variables to init, get and set texts. Start logger and manage allowed 
Meshtastic Gateways.
'''

import time
import logging

TEXT = 'init'

# Init Logger
logger = logging.getLogger(__name__)
logging.basicConfig(filename='nostrastic.log', level=logging.INFO)
current_time = time.localtime()
now = time.strftime("(%d/%m/%Y - %H:%M:%S)", current_time)


def init_log():
    '''
    Header text for the log when Nostrastic start.
    '''
    logger.info('')
    logger.info('################################################')
    logger.info('#### Nostrastic Started: %s', now)
    logger.info('################################################')


def end_log():
    '''
    Footer text for the log when Nostrastic stop.
    '''
    logger.info('')
    logger.info('################################################')
    logger.info('Nostrastic Finished: %s', now)
    logger.info('################################################')


def write_info_log(log_message):
    '''
    Write formatted info messsages in the Log file
    '''
    logger.info('%s: %s', now, log_message )


def write_error_log(log_message):
    '''
    Write formatted error messages in the Log file
    '''
    logger.error('%s: %s', now, log_message)


### Managing Text from MQTT Server to Nostr to avoid resend/publish the same message
def init_text():
    '''
    Set the initial text when the Script start.
    '''
    global text
    text = TEXT


def set_text(new_text):
    '''
    Set a new text string to send in the next message
    '''
    global text
    text = new_text


def get_text():
    '''
    Get the current value of text
    '''
    return text


### Managing Text from Nostr to MQTT Server to avoid resend/publish the same message
def init_nostr_text():
    '''
    Set the initial text when the Script start.
    '''
    global nostr_text
    nostr_text = TEXT


def set_nostr_text(new_text):
    '''
    Set a new text string to send in the next message
    '''
    global nostr_text
    nostr_text = new_text


def get_nostr_text():
    '''
    Get the current value of text
    '''
    return nostr_text


## Managing the current Gateway from the first Meshtastic message is sent
def set_gateway_dec(gateway):
    '''
    Set as a allowed Meshtastic Gateway when first message is sent from Meshtastic Device to Nostr
    decimal format.
    '''
    global mqtt_gateway_dec
    mqtt_gateway_dec = gateway
    return mqtt_gateway_dec


def get_gateway_dec():
    '''
    Get allowed Meshtastic Gateway in Decimal format
    '''
    return str(mqtt_gateway_dec)


def set_gateway_hex(gateway):
    '''
    Set as a allowed Meshtastic Gateway when first message is sent from Meshtastic Device to Nostr
    hexadecimal format.
    '''
    global mqtt_gateway_hex
    mqtt_gateway_hex = gateway
    return mqtt_gateway_hex


def get_gateway_hex():
    '''
    Get allowed Meshtastic Gateway in Hexadecimal format
    '''
    return str(mqtt_gateway_hex)

