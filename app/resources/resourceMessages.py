import time
import sys
import json
import falcon
from falcon import media
from falcon.media.validators import jsonschema as fjsonschema
import logging
from kafka import KafkaAdminClient
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
from datetime import datetime, timezone

logging.info("Importing in resources")

from jsonschema import validate, ValidationError, SchemaError
from kafka.errors import KafkaError


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s - in %(filename)s - Func: %(funcName)s - Line: %(lineno)d - Thread: %(threadName)s')


ALLOWED_DATA_TYPE={'application/json'}

json_schema = {
    "type": "object",
    "properties": {
        "numbers": {
            "type": "array",
            "items": {"type": "integer"}
        }
    },
    "required": ["numbers"]
}

fjson_schema = {
    "type": "object",
    "properties": {
        "numbers": {
            "type": "array",
            "items": {
                "type": "integer"}
            }
    },
    "required": ["numbers"]
}

class ProducerHandling:
    def __init__(self, kafka_producer):
        self.kafka_producer=kafka_producer

    def on_success(self, producer_records, topic):
        logging.info(f"Success. Messages succesfuly sent to topic: {topic}"
                     f"Topic: {producer_records.topic}"
                     f"Offset: {producer_records.offset}")

    def on_errors(self, exc, topic):
        logging.error(f"Sending messages failed due to: {exc}")

    def send_message(self, topic, message_value):
        try:
            future=self.kafka_producer.send(topic, value=message_value)
            future.add_callback(self.on_success, topic=topic)
            future.add_errback(self.on_errors, topic=topic)
        except Exception as exc:
            logging.error(f"Failed to send message due to: {exc}")
def data_validation(req, resp, resource, params):
    if req.content_length in (None, 0):
        msg='data is empty.'
        logging.info(f"Data validation, error: {msg}")
        raise falcon.HTTPBadRequest(title='Bad request', description=msg)
    
    elif req.content_type not in ALLOWED_DATA_TYPE:
        msg='Data is not valid. Content-type be a json format!'
        logging.info(f"Data validation, error: {msg}")
        raise falcon.HTTPBadRequest(title='Bad request', description=msg)
    
    try:
        data=req.get_media() #Parsing JSON body
        if data is None:
            msg = 'data is empty.'
            logging.info(f"Data validation, error: {msg}")
        else:
            logging.info(f"Received the data: {data}")

    except json.JSONDecodeError as e:
        # Handle the JSON decoding error
        logging.info(f"JSONDecodeError: {str(e)}")
        raise falcon.HTTPBadRequest(title='Bad request', description=f"Invalid JSON: {str(e)}")

    except falcon.HTTPInvalidHeader as e:
        # Handle specific exception for invalid header
        logging.info(f"HTTPInvalidHeader: {str(e)}")

        raise falcon.HTTPBadRequest(title='Bad request', description=f"Invalid JSON: {str(e)}")

    except Exception as e:
        logging.info(f"Exception: {e}")
        raise falcon.HTTPInternalServerError(description=f"An unexpected error occurred: {str(e)}")

    try: #Nije mi radilo u početku
        # Validate the parsed JSON data against a schema
        logging.info(f"Validating instance: {data} With schema: {json_schema}")
        validate(instance=data, schema=json_schema) #proradilo
        logging.info("Validation succesfull")
        req.context['validated_data'] = data  # To be able to usit in on_post or and any other method

    except ValidationError as e:
        logging.info(f"ValidationError: {str(e)}")
        raise falcon.HTTPBadRequest(title='Bad request', description=f"Validation error: {str(e)}")

    except SchemaError as e:
        logging.info(f"SchemaError: {str(e)}")
        raise falcon.HTTPBadRequest(title='Bad request', description=f"Schema error: {str(e)}")

    except Exception as e:
        logging.info(f"An unexpected error occurred: {str(e)}")
        raise falcon.HTTPInternalServerError(description=f"An unexpected error occurred: {str(e)}")
class Messages(ProducerHandling):
    def __init__(self, kafka_producer, kafka_config):
        super().__init__(kafka_producer)
        self.kafka_config = kafka_config

    @falcon.before(data_validation)
    def on_post(self, req, resp):

        data = req.context['validated_data'] #Parsing from data validation method
        numbers = data.get('numbers', {})
        response_data = {
            "message": "Data is valid"
        }
        resp.media = response_data
        resp.status = falcon.HTTP_201
        # resp.data = json.dumps(response_data)
        # resp.context = numbers <<- store additional data that might be useful for logging, caching etc
        # resp.text=json.dumps(response_data) #return text with  Content-Type header set to text/plain

        msg = {
            "numbers": numbers,
            "eventTimestamp": datetime.now(timezone.utc).isoformat()
        }

        first_topic = self.kafka_config["first_kafka_topic"]
        message = json.dumps(msg).encode('utf-8')
        self.send_message(first_topic, message)

class Messagesv2(ProducerHandling): #Naj

    def __init__(self, kafka_producer, kafka_config):
        super().__init__(kafka_producer)
        self.kafka_config = kafka_config
    
    @fjsonschema.validate(fjson_schema)
    def on_post(self, req, resp):
        if req.content_length in (None, 0):
            raise falcon.HTTPBadRequest('No message', 'Nothing to parse')

        try:    
            data=req.get_media()
            numbers2=data['numbers']

            logging.info(f"Checking if numbers are extracted: {numbers2}") #OK
            numbers = data.get('numbers', {})
            response_data = {
                "message": "Data is valid"
            }
            resp.status = falcon.HTTP_201
            resp.media = response_data

        except json.JSONDecodeError as e: #Todo Checke
            # Handle the JSON decoding error
            logging.error(f"Exception with json.JSONDecodeError {e}")
            resp.status = falcon.HTTP_400
            resp.text = "Internal server error: " + str(e)
            return

        except falcon.HTTPInvalidHeader as e:
            # Handle specific exception for invalid header
            resp.status = falcon.HTTP_400
            resp.text = "Invalid request header"
            return

        except falcon.HTTPBadRequest as e:
            # Handle specific exception for bad request
            resp.status = falcon.HTTP_400
            resp.text = "Bad request: " + str(e)
            return

        except Exception as e:
            # Handle any other unexpected exceptions
            resp.status = falcon.HTTP_500
            resp.text = "Internal server error: " + str(e)
            return

        if numbers:
            msg = {
                "numbers": numbers,
                "eventTimestamp": datetime.now(timezone.utc).isoformat()
            }

            first_topic = self.kafka_config["first_kafka_topic"]
            message_value = json.dumps(msg).encode('utf-8')
            self.send_message(first_topic, message_value=message_value)
class FinalMessage:
    def __init__(self, consumer_wrapper, kafka_config):
        self.consumer_wrapper = consumer_wrapper
        self.kafka_c_config=kafka_config
        self.final_kafka_topic= kafka_config['final_kafka_topic']
        self.max_messages=kafka_config['max_messages']
        self.consumer_timeout_ms=kafka_config['consumer_timeout_ms']

    def create_consumer(self):
        try:
            consumer = self.consumer_wrapper(bootstrap_servers=self.kafka_c_config['bootstrap_servers'],
                                             auto_offset_reset=self.kafka_c_config['auto_offset_reset'],
                                             group_id=self.kafka_c_config['group_id2'],
                                             consumer_timeout_ms=self.kafka_c_config['consumer_timeout_ms'],
                                             value_deserializer=lambda m: json.loads(m.decode("utf-8")))
            logging.info("Kafka consumer created successfully.")
            return consumer
        except KafkaError as e:
            logging.error(f"KafkaError when creating consumer: %s", e)
            raise falcon.HTTPInternalServerError(description="Consumer creation failed.")
        except Exception as e:
            logging.error(f"Error {e} when creating consumer")
            raise falcon.HTTPInternalServerError(description="Consumer creation failed.")
    '''
    def list_topics(self):
        try:
            admin_client = KafkaAdminClient(bootstrap_servers=self.kafka_c_config['bootstrap_servers'])
            topics = admin_client.list_topics()
            logging.info(f"Available topics: {topics}")
            return topics
        except KafkaError as e:
            logging.error(f"KafkaError when listing topics: {e}")
            return None
        except Exception as e:
            logging.error(f"Error {e} when listing topics")
            return None'''

    def deserialize(self, message):
        return json.loads(message.decode('utf-8'))

    def on_get(self, req, resp):
        start_time=time.time()

        try:
            self.consumer = self.create_consumer()  # Use the create_consumer method
        except falcon.HTTPInternalServerError as e: #Todo mislim da mi ne treba
            resp.status = falcon.HTTP_500
            resp.media = {"error": str(e)}
            return

        try:
            self.consumer.subscribe([self.final_kafka_topic])
            # Check if subscription was successful
            subscribed_topics = list(self.consumer.subscription())

            ''' To check if subscribed to correct topic, but mybe time consuminh
            if self.final_kafka_topic not in subscribed_topics:
                logging.error(f"Consumer not subscribed to final_numbers. Subscribed to: {subscribed_topics}")
                resp.status = falcon.HTTP_500
                resp.media = {"error": f"Consumer not subscribed to the self.final_kafka_topic: {self.final_kafka_topic}."}
                return'''

            final_messages=[]

            for msg in self.consumer:
                #consumed_value = self.deserialize(msg.value)
                final_messages.append(msg.value)
                if len(final_messages) >= self.max_messages: #TODO test with max_poll_records
                    logging.info(f"Returning max number of messages")
                    break

                if time.time() - start_time > 2: #TODO REMOVE THIS AND USE ONLY TIME OUT
                    logging.info(f"Max time reached: {time.time() - start_time}")
                    break

            logging.info(f"Time passed: {time.time() - start_time}")

            if len(final_messages) == 0:
                logging.info("No messages found")
                #resp.status = falcon.HTTP_204 No content, but then ther is no media
                resp.media = {"message": "No messages"}

            else:
                logging.info("Number of messages: %d", len(final_messages))
                logging.info(f"Final messages: {final_messages}")
                resp.media = final_messages
                resp.content_type = falcon.MEDIA_JSON
                # How to get indentation
                resp.status = falcon.HTTP_200

        except KafkaError as e:
            logging.error(f"KafkaError during message consumption: {e}")
            resp.status = falcon.HTTP_500
            resp.media = {"error": "Internal Server Error: Kafka consumption failed"}

        except Exception as exc:
            logging.error(f"Subscribing failed due to: {exc}")
            resp.status = falcon.HTTP_500
            resp.media = {"error": exc}
        finally:
            self.consumer.close()
            logging.info(f"Closing consumer")

class Messagesbasic():
    def __init__(self, kafka_producer, kafka_config):
        self.kafka_producer = kafka_producer
        self.kafka_config=kafka_config

    def on_get(self, req, resp):
        raise falcon.HTTPMethodNotAllowed(allowed_methods=['POST'])

    def on_post(self, req, resp):
        if req.content_length in (None, 0):
            logging.info(f"Body is empty:")
            raise falcon.HTTPBadRequest(title='Bad request', description='Body is empty') #Title, desc

        try:
            # Load the JSON data from the request body
            data = req.get_media()
            # Falcon uses JSONHandler to handle application/json content types by default:
            # falcon.media.JSONHandler()
            # req.stream.read()? => Don't do after req.get.media() :
            # bcs Falcon only processes request media the first time it is referenced
            logging.info("Media extracted " + str(media))
            # Todo

        except falcon.errors.MediaMalformedError as e:
            logging.info(f"MediaMalformedError: Invalid media format: {str(e)}")
            raise falcon.HTTPBadRequest(title='Bad request', description=f"Invalid JSON format: {str(e)}")

        except json.JSONDecodeError as e:
            logging.info(f"JSONDecodeError: Invalid JSON: {str(e)}")
            # Handle the JSON decoding error
            raise falcon.HTTPBadRequest(title='Bad request', description=f"Invalid JSON: {str(e)}")

        except falcon.HTTPInvalidHeader as e:
            # Handle specific exception for invalid header
            logging.info(f"HTTPInvalidHeader: {str(e)}")
            raise falcon.HTTPBadRequest(title='Bad request', description=f"HTTPInvalidHeader: {str(e)}")

        except falcon.HTTPBadRequest as e:
            logging.info(f"falcon.HTTPBadRequest: {str(e)}")
            # Handle specific exception for bad request
            raise falcon.HTTPBadRequest(title='Bad request', description=f"HTTPBadRequest: {str(e)}")

        except Exception as e:
            logging.info(f"General exception when reading the numbers: {str(e)}")
            raise falcon.HTTPInternalServerError(description=f"An unexpected error occurred: {str(e)}")

        try:
            # Validate the JSON data using json_schema
            logging.info(f"Validating instance: {data},\nWith schema: {json_schema}")
            validate(instance=data, schema=json_schema)  # proradio
            logging.info("Validation successful! Extracting numbers from request")

            # Extract the 'numbers' arr
            numbers = data.get('numbers', [])

            response_data = {
                "numbers": numbers,
                "message": "Data is valid"
            }
            resp.media = response_data
            resp.status = falcon.HTTP_200  # New resource created

            msg = {
                "numbers": numbers,
                "eventTimestamp": datetime.now(timezone.utc).isoformat()
            }

            logging.info("msg is:" + str(msg))

        except ValidationError as e:
            logging.info(f"ValidationError: {str(e)}")
            raise falcon.HTTPBadRequest(title='Invalid data', description=f"{str(e)}")
            # Title, desc

        except SchemaError as e:
            logging.info(f"SchemaError: {str(e)}")
            raise falcon.HTTPBadRequest(title='Bad request', description=f"Schema error: {str(e)}")

        except Exception as e:
            logging.info(f"General exception when reading the numbers: {str(e)}")
            raise falcon.HTTPInternalServerError(description=f"An unexpected error occurred: {str(e)}")


        first_topic = self.kafka_config["first_kafka_topic"]
        message_value = json.dumps(msg).encode('utf-8')

        try:
            self.kafka_producer.send(first_topic,
                                     value=message_value)
            # Todo callback=delivery_callback
            # Messagev2
            logging.info(f"Message produced to {first_topic}")
        except Exception as e:
            logging.error("Message failed to be produced: " +str(e))

        # resp.data = json.dumps(response_data)
        # resp.context = numbers <<- store additional data that might be useful for logging, caching etc
        # resp.text=json.dumps(response_data) #return text with  Content-Type header set to text/plain
        # NOTE WHEN raise exception Falcon autmatically handles exceptiona and generates HTTP repsonse
        # On 'on_post) method will not be executed