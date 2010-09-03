# middleware to log any requests to DB
from bio.models import Log, CrudLog


class RequestLog:

    def process_request(self, request):
        mr = Log(method=request.method, url=request.path)
        mr.save()


def log_save(sender, **kwargs):
    print kwargs

    action = "save"

    # if kwargs['created']:
        # action = "create"

    cl = CrudLog(model=sender, action=action)
    cl.save()


def log_delete(sender, **kwargs):
    cl = CrudLog(model=sender, action="delete")
    cl.save()
