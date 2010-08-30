# middleware to log any requests to DB

from mybio.bio.models import Log

class RequestLog:
    def process_request(self, request):
        mr = Log(method=request.method, url=request.path)
        mr.save()
