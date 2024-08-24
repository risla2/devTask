#!/usr/bin/env python3

import json
import os
from kafka3 import KafkaProducer, KafkaConsumer
import time
#from kafka import KafkaAdminClient
#from kafka.errors import KafkaError
from argparse import ArgumentParser, FileType
import configparser

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ini_path=('config.ini')
config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation()) #TODO Radi sad
# Check if the file exists
if not os.path.isfile(ini_path):
    logging.info("Filepath: '" + ini_path +  "' does not exist. Adding kafka_res/config.ini to current wd")
    ini_path = os.path.join(os.getcwd(), 'kafka_res/config.ini')
    if not os.path.isfile(ini_path):
        logging.info("Netiher the file " + ini_path + " exist.")
        ini_path = os.path.join(os.getcwd(), 'app/kafka_res/config.ini')
    else:
        logging.info("File path '" + ini_path + "' exist " + os.getcwd()+"/kafka_res/config.ini")

else:
    logging.info(f"The file '" + ini_path + "' found in: " + os.getcwd())


# Read the configuration file
try:
    config.read(ini_path)
except Exception as e:
    logging.error("Check kafka_rep.py " + ini_path + "is not found")

#Print sections
if config.sections():
    logging.info(f"Config sections found in '{ini_path}': '{config.sections()}'")
    '''
    for section in config.sections():
        logging.info(f"Section [{section}]:")
        for key, value in config.items(section):
            logging.info(f"{key} = {value}")
    try:
        acks = config['Producer']['acks']
        logging.info(f"Acks: {acks}")
    except configparser.InterpolationMissingOptionError as e:
        logging.info(f"Interpolation error: {e}")
    '''
else:
    logging.info(f"No sections found in '{ini_path}'.")

def serializer(message):
    return json.dumps(message.encode('utf-8'))

def deserializer(message):
    return json.loads(message.decode('utf-8'))

apikey = config['Security']['api_key']
kafka_config = {
    'bootstrap_servers':config['Kafka']['bootstrap_servers'],
    'first_kafka_topic':config['Kafka']['first_kafka_topic'],
    'final_kafka_topic': config['Kafka']['final_kafka_topic'],
    'auto_offset_reset' : config['Consumer']['auto_offset_reset'],
    'consumer_timeout_ms' : int(config['Consumer']['consumer_timeout_ms']),
    'max_messages' : int(config['Kafka']['max_messages']),
    'group_id' : config['Kafka']['group_id'],
    'acks' : config['Producer']['acks']
}
kafka_p_config = {
    'bootstrap_servers': kafka_config['bootstrap_servers'],
    'acks': kafka_config['acks']
}

kafka_c_config = {
    'bootstrap_servers': kafka_config['bootstrap_servers'],
    'group_id': kafka_config['group_id'],
    'auto_offset_reset': kafka_config['auto_offset_reset'],
}

def create_kafka_producer():
    logging.info("Creating producer for" + kafka_p_config['bootstrap_servers'])
    return KafkaProducer(bootstrap_servers=kafka_p_config['bootstrap_servers'])

def create_kafka_consumer(**kwargs):
    if not kwargs:
        logging.info("Returning consumer from kafka_rep.py " + kafka_c_config['bootstrap_servers'])
        return KafkaConsumer(bootstrap_servers=kafka_c_config['bootstrap_servers'], auto_offset_reset=auto_offset_reset, group_id=group_id)
    else:
        for key, value in kwargs.items():
            logging.info(f"KEY: {key}, VALUE: {value}")

        logging.info("Returning consumer with kwargs from kafka_rep.py " + kafka_c_config['bootstrap_servers'])

        return KafkaConsumer(**kwargs)

def delivery_callback2(err, msg):
    if err:
        logging.error('ERROR: Message failed delivery: {}'.format(err))
    else:

        logging.info("Produced event to topic {topic}: value = {value:12}".format(
            topic=msg.topic(),  value=msg.value().decode('utf-8')))

#confluent_producer.produce(PRODUCER_TOPIC, value=message_value,callback=delivery_callback)
