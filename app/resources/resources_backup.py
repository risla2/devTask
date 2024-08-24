'''
req (Request object): This parameter represents the HTTP request made by the client. It contains information such as the request method (GET, POST, etc.), headers, query parameters, form data, and the request body. The req object provides methods and properties to access and manipulate this information.

resp (Response object): This parameter represents the HTTP response that will be sent back to the client. It allows you to set response headers, status codes, and response body data. The resp object provides methods and properties to manipulate the response before sending it back to the client.

These parameters are passed to Falcon route handler methods (such as on_get, on_post, etc.) so that you can access and modify both the request and response objects as needed to handle the client's request appropriately.

By convention, Falcon route handler methods typically take req and resp as parameters, but you can name them differently if you prefer. However, it's recommended to stick with req and resp to maintain clarity and consistency with Falcon's conventions.
'''


import io
import re
import os
import json
import falcon
#import logging
from falcon import media
from falcon.media.validators import jsonschema as fjsonschema
from jsonschema import validate


# Create a logger object
#logger = logging.getLogger(__name__)
handlers = media.Handlers()

ALLOWED_DATA_TPYE={'application/json'}

json_schema = {
    "type": "object",
    "properties": {
        "message": {
            "type": "object",
            "properties": {
                "numbers": {"type": "array", "items": {"type": "integer"}}
            },
            "required": ["numbers"]
        }
    }
}

json_schemav2 = {
    "type": "object",
    "properties": {
        "message": {
            "type": "object",
            "properties": {
                "numbers": {"type": "array", "items": {"type": "integer"}}
            },
            "required": ["numbers"]
        }
    }
}

fjson_schema = {
    "type": "object",
    "properties": {
        "message": {
            "type": "object",
            "properties": {
                "numbers": {"type": "array", "items": {"type": "integer"}}
            },
            "required": ["message","numbers"]
        }
    }
}


def data_validation(req, resp, resource, params):
    if req.content_length in (None, 0):
        msg='data is empty.'
        raise falcon.HTTPBadRequest(title='Bad request', description=msg)
    
    elif req.content_type not in ALLOWED_DATA_TPYE:
        msg='Data is not valid. Must be a json format!'
        raise falcon.HTTPBadRequest(title='Bad request', description=msg)
    
    try:
        obj=req.get_media('message')
    except json.JSONDecodeError as e:
        # Handle the JSON decoding error
        resp.status = falcon.HTTP_400
        resp.text = "Internal server error: " + str(e)

    except falcon.HTTPInvalidHeader as e:
        # Handle specific exception for invalid header
        resp.status = falcon.HTTP_400
        resp.text = "Invalid request header"
    except falcon.HTTPBadRequest as e:
        # Handle specific exception for bad request
        resp.status = falcon.HTTP_400
        resp.text = "Bad request: " + str(e)
    except Exception as e:
        # Handle any other unexpected exceptions
        resp.status = falcon.HTTP_500
        resp.text = "Internal server error: " + str(e)
        # Log the exception for debugging
        #logger.exception("An error occurred while processing the request")


    try:
        fjsonschema.validate(obj, fjson_schema)
        resp.media = obj
    except fjsonschema.exceptions.ValidationError as msg:
        raise falcon.HTTPBadRequest(title='Bad request', description=msg)
    except fjsonschema.exceptions.SchemaError as msg:
        raise falcon.HTTPBadRequest(title='Bad request', description=msg)
    


def message_validator(data, json_schemav2):
    try:
        fjsonschema.validate(data, json_schemav2)
    except fjsonschema.exceptions.ValidationError as msg:
        raise falcon.HTTPBadRequest(title='Bad request', description=msg)
    except fjsonschema.exceptions.SchemaError as msg:
        raise falcon.HTTPBadRequest(title='Bad request', description=msg)

    
class Resource:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_TEXT
        resp.text = 'Body: on_get loaded sucessfully!'

    def on_post(self, req, resp):
        resp.status = falcon.HTTP_201

class Messages:
    '''def parse_json(req, resp, resource, params):
        if req.content_length in (None, 0):
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        body = req.stream.read()
        try:
            req.context['data'] = json.loads(body.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPError(falcon.HTTP_753,
                                'Malformed JSON',
                                'Could not decode the request body. The '
                                'JSON was incorrect or not encoded as '
                                'UTF-8.')'''
    def on_get(self, req, resp):
        
        resp.status = falcon.HTTP_200
        #resp.content_type = falcon.MEDIA_MSGPACK
        resp.content_type= falcon.MEDIA_JSON
        resp.text = (
            "List of Messages"
            )
        

    def on_post(self, req, resp):
        # print(req["content_type"])
        #TODO If req.content_lenght is 0 or None
        if req.content_length in (None, 0):
            raise falcon.HTTPBadRequest('Body is empty',
                                         'Nothing to parse')
        #resp.content_type= falcon.MEDIA_JSON
        #resp.content_type = 'application/json' 
        resp.content_type = req.accept

        # Deserialize the request body based on the Content-Type
        #   header in the request, or the default media type
        #   when the Content-Type header is generic ('*/*') or
        #   missing.
           
        # The framework will look for a media handler that matches
        #   the response's Content-Type header, or fall back to the
        #   default media type (typically JSON) when the app does
        #   not explicitly set

        chunk_size=1024 # Becuses n numbers in array
        '''try:
            while True:
                chunk=req.bounded.stream.read(chunk_size).decode('utf-8')
                if not chunk:
                    break
                numbers.append(chunk)

            numbers_str = ''.join(numbers)
            parsed_numbers = json.loads(numbers_str)
            print(parsed_numbers)
        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect or not encoded as '
                                   'UTF-8.')'''
        try:    
            # Load the JSON data from the request body
            obj=req.get_media('message')
            # body_bytes =req.stream.read() doesn't work after req.get.media() : o avoid unnecessary overhead, Falcon will only process request media the first time it is referenced
            #body_json=json.loads(obj.body_bytes('utf-8'))
            print("obj:", obj) #OK            
            #Basic validation jsonschema import validate
            try:
                validate(obj, json_schema)
                resp.media = {"message": "Data is valid"}
            except Exception as e:
                resp.status = falcon.HTTP_400
                resp.media = {"error": str(e)}

            #message_validator(obj, json_schema)

            # Extract the 'numbers' dictionary from the body
            print("Extract the list of numbers from the JSON data") 
            numbers = obj.get('numbers', {})
            print("numbers_str:", numbers) #message_str: '{numbers:[1,2,3,4,5,6]}'

            message_resp="Numbers parsion succesfull!"
            response_data = {
                "body_json": obj,
                "numbers": numbers,
                "message_resp":message_resp,
            }

            '''
            resp.media = {
                "numbers": numbers,
                "letters": letters
            }
            resp.status = falcon.HTTP_200
            '''
            resp.status = falcon.HTTP_201
            #resp.content_type = 'application/json' 
            #resp.content_type = req.accept 
            resp.data = json.dumps(response_data) #raise TypeError(f'Object of type {o.__class__.__name__} TypeError: Object of type bytes is not JSON serializable
            resp.context = numbers
            resp.media = obj
            resp.text=json.dumps(response_data)

        except json.JSONDecodeError as e:
            # Handle the JSON decoding error
            resp.status = falcon.HTTP_400
            resp.text = "Internal server error: " + str(e)

        except falcon.HTTPInvalidHeader as e:
            # Handle specific exception for invalid header
            resp.status = falcon.HTTP_400
            resp.text = "Invalid request header"
        except falcon.HTTPBadRequest as e:
            # Handle specific exception for bad request
            resp.status = falcon.HTTP_400
            resp.text = "Bad request: " + str(e)
        except Exception as e:
            # Handle any other unexpected exceptions
            resp.status = falcon.HTTP_500
            resp.text = "Internal server error: " + str(e)
            # Log the exception for debugging
            #logger.exception("An error occurred while processing the request")


class Messagesv2:
    def on_get(self, req, resp):        
        resp.status = falcon.HTTP_200
        resp.content_type= falcon.MEDIA_JSON
        resp.text = (
            "List of Messages"
            )
        
    
    @falcon.before(data_validation)
    def on_post(self, req, resp):
        #TODO If req.content_lenght is 0 or None
        if req.content_length in (None, 0):
            raise falcon.HTTPBadRequest('Body is empty',
                                         'Nothing to parse')
        resp.content_type = req.accept
        chunk_size=1024 # Becuses n numbers in array


        obj=resp.media
        print("body_json:", obj) #OK            
        #Basic validation jsonschema import validate
        try:
            validate(obj, json_schema)
            resp.media = {"message": "Data is valid"}
        except Exception as e:
            resp.status = falcon.HTTP_400
            resp.media = {"error": str(e)}


        # Extract the 'numbers' dictionary from the body
        print("Extract the list of numbers from the JSON data") 
        numbers = obj.get('numbers', {})
        print("numbers_str:", numbers) #message_str: '{numbers:[1,2,3,4,5,6]}'

        message_resp="Numbers parsion succesfull!"
        response_data = {
            "body_json": obj,
            "numbers": numbers,
            "message_resp":message_resp,
        }

        
        resp.status = falcon.HTTP_201
        resp.data = json.dumps(response_data) #raise TypeError(f'Object of type {o.__class__.__name__} TypeError: Object of type bytes is not JSON serializable
        resp.context = numbers
        resp.media = obj
        resp.text=json.dumps(response_data)



class Messagesv3:

    def on_get(self, req, resp):
        
        resp.status = falcon.HTTP_200
        #resp.content_type = falcon.MEDIA_MSGPACK
        resp.content_type= falcon.MEDIA_JSON
        resp.text = (
            "List of Messages"
            )
    
    @fjsonschema.validate(fjson_schema)
    def on_post(self, req, resp):
        # print(req["content_type"])
        #TODO If req.content_lenght is 0 or None
        if req.content_length in (None, 0):
            raise falcon.HTTPBadRequest('Body is empty',
                                         'Nothing to parse')
        resp.content_type = req.accept

        try:    
            obj=req.get_media('message')
            numbers=obj['message']['numbers']
            print("numbers:", numbers) #OK
            resp.status = falcon.HTTP_201
            resp.data = json.dumps(response_data) #raise TypeError(f'Object of type {o.__cla            
            # Extract the 'numbers' dictionary from the body
            print("Extract the list of numbers from the JSON data") 
            numbers = obj.get('numbers', {})
            print("numbers_str:", numbers) #message_str: '{numbers:[1,2,3,4,5,6]}'

            message_resp="Numbers parsion succesfull!"
            response_data = {
                "body_json": obj,
                "numbers": numbers,
                "message_resp":message_resp,
            }

            resp.status = falcon.HTTP_201
            resp.data = json.dumps(response_data) #raise TypeError(f'Object of type {o.__class__.__name__} TypeError: Object of type bytes is not JSON serializable
            resp.context = numbers
            resp.media = obj
            resp.text=json.dumps(response_data)

        except json.JSONDecodeError as e:
            # Handle the JSON decoding error
            resp.status = falcon.HTTP_400
            resp.text = "Internal server error: " + str(e)

        except falcon.HTTPInvalidHeader as e:
            # Handle specific exception for invalid header
            resp.status = falcon.HTTP_400
            resp.text = "Invalid request header"
        except falcon.HTTPBadRequest as e:
            # Handle specific exception for bad request
            resp.status = falcon.HTTP_400
            resp.text = "Bad request: " + str(e)
        except Exception as e:
            # Handle any other unexpected exceptions
            resp.status = falcon.HTTP_500
            resp.text = "Internal server error: " + str(e)
            # Log the exception for debugging
            #logger.exception("An error occurred while processing the request")