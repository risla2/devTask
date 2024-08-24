
import falcon
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Importing in auth_middlerware.py")
class ApiKeyMiddleware:
    def __init__(self, api_key):
        self.required_api_key = api_key

    def process_request(self, req, resp):
        api_key = req.get_header('Authorization')  # Assuming API key is passed in the header
        if api_key is None:
            description = 'Please provide an auth token as part of the request.'
            resp.status=falcon.HTTP_401
            raise falcon.HTTPUnauthorized(
                title='Auth token required',
                description=description,
            )

        if api_key != self.required_api_key:
            resp.status = falcon.HTTP_403
            description='Invalid API Key'
            raise falcon.HTTPUnauthorized(title='Wrong API key', description=description)


    def authorize(self, req):
        #TODO
        pass

    def process_response(self, req, resp, resource, req_succeeded):
        #TODO
        pass
