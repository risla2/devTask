# !/usr/bin/env python3

import sys
import logging
from configparser import ConfigParser
from argparse import ArgumentParser, FileType

from datetime import datetime,timezone
import logging
import json
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s - in %(filename)s - Func: %(funcName)s - Line: %(lineno)d - Thread: %(threadName)s')

#Import producuer, consumer, config and apikey depending on the app path
#Todo Fix in the dockerfile?

try:
    from kafka_rep import create_kafka_producer, create_kafka_consumer, kafka_config, apikey
except Exception as e:
    logging.info(f"Importing from kafka_rep failed: {e}")
    from app.kafka_res.kafka_rep import create_kafka_producer, create_kafka_consumer, kafka_config
def serializer(message):
    return json.dumps(message).encode('utf-8')
def deserializer(message):
    return json.loads(message.decode('utf-8'))
def main():

    kafka_producer = create_kafka_producer()
    logging.info(str(kafka_producer) + "created")


    logging.info("Main of kafka_rep.py")

    first_kafka_topic = kafka_config['first_kafka_topic']
    final_kafka_topic = kafka_config['final_kafka_topic']
    try:
        #kafka_consumer = create_kafka_consumer()
        kafka_consumer = create_kafka_consumer(bootstrap_servers=kafka_config['bootstrap_servers'],
                                               auto_offset_reset=kafka_config['auto_offset_reset'],
                                               group_id=kafka_config['group_id1'])
        logging.info("Consumer created FOR kafka_python.py: " + str(kafka_consumer) + "broker")
        kafka_consumer.subscribe([first_kafka_topic])
        logging.info("Consumer subscribed FOR kafka_python.py " + str(first_kafka_topic))
    except Exception as e:
        logging.error("Consumer not created FOR kafka_python.py due to : " + str(e))
        return

    try:
        #while True:
        #msg = kafka_consumer.poll(1.0)
        logging.info("Starting CONSUMING messages in kafka_python.py" + str(kafka_consumer))

        for msg in kafka_consumer:
            logging.info(f"Message received {msg.value}, deserialized with deserializer {deserializer(msg.value)}")
            consumed_value = deserializer(msg.value)
            logging.info(f"Consumed values: {consumed_value}")

            try:
                logging.info("Consumed event from topic {topic}: value = {value:12}".format(topic=msg.topic, value=str(consumed_value)))
            except Exception as excc:
                logging.error(f"Error u liniji 195, {excc}")


            processed_timestamp = datetime.now(timezone.utc)
            enriched = {"msg_offset": msg.offset,
                        "numbers": consumed_value.get("numbers", []),
                        "sum": sum(consumed_value.get("numbers", [])),
                        "eventTimestamp": consumed_value.get("eventTimestamp"),
                        "timestamp": processed_timestamp.isoformat()}

            logging.info(f"Consumed messages has been enriched: " + str(enriched) + " and will be sent to " + final_kafka_topic)

            message_value = json.dumps(enriched).encode('utf-8')
            try:
                kafka_producer.send(final_kafka_topic, value=message_value)
                #TODO Add callbac
                logging.info(f"Enriched message {message_value} sent to TOPIC: {final_kafka_topic}")
            except Exception as e:
                logging.error("Msg not send: " + str(e))

    except KeyboardInterrupt:
        pass
    except Exception as exc:
        logging.error(f"Error when attempted to read messages in kafka_python.py: {exc}")
    finally:
        try:
            kafka_consumer.close()
            logging.info("Kafka consumer closed")
        except Exception as e:
            logging.error("Kafka consumer failed to close")

    #TODO
    #keyboad interruption
    #delivery callback
    # Poll for new messages from Kafka
    #kafka_consumer.subscribe([topic_name])
    #kafka_consumer.subscribtion()

if __name__ == '__main__':
    main()

