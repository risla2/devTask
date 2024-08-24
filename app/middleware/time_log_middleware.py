import time

class ResponseLoggerMiddleware:
    def process_request(self, req, resp):
        req.context['start_time'] = time.time()

    def process_response(self, req, resp, resource, req_succeeded):
        print("Processing response in response logger middleware\n")

        if 'start_time' in req.context:
            #end_time = time.time()
            response_time = time.time() - req.context['start_time']
            resp.set_header('responseTime', round(response_time,2))
        else:
            resp.set_header('responseTime', '0')