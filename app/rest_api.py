#!/usr/bin/env python3

import os
from waitress import serve
import falcon
#from dotenv import load_dotenv

#load_dotenv(override=True)
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s - in %(filename)s - Func: %(funcName)s - Line: %(lineno)d - Thread: %(threadName)s')

from resources.resourceMessages import Messagesbasic, Messages, Messagesv2, FinalMessage
from middleware.auth_middleware import ApiKeyMiddleware
from middleware.time_log_middleware import ResponseLoggerMiddleware
from kafka_res.kafka_rep import create_kafka_producer, create_kafka_consumer, apikey, kafka_config  # <---from kafka_res.kafka_python import c_producer

if __name__ == "__main__":

    app = falcon.App(middleware=[ApiKeyMiddleware(apikey), ResponseLoggerMiddleware()])

    PORT=8000
    app.add_route('/message', Messages(create_kafka_producer(), kafka_config)) #@falcon.before(data_validation) - def data_validation(req, resp, resource, params):
    app.add_route('/messagev2', Messagesv2(create_kafka_producer(), kafka_config)) #fjsonschema.validate from falcon.media.validators -
    app.add_route('/final', FinalMessage(create_kafka_consumer, kafka_config)) #Read from final topic withing timeout in seconds
    # app.add_route('/messagebasic', Messagesbasic(create_kafka_producer(), kafka_config))
    # ->validate(instance=media, schema=json_schema) -> Basic validation

    logging.info("Starting rest-api started on port:" + str(PORT))
    serve(app, host='0.0.0.0', port=PORT)
