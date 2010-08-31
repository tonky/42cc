import time, datetime
from twill.commands import find, code, title, go
from tddspry import NoseTestCase
from bio.models import Log, Bio

class WebTest(NoseTestCase):
    start_live_server = True

    def test_middleware_logging(self):
        go("http://localhost:8000/test/me/")

        req = Log.objects.order_by('-date')[0] # last by date

        now = datetime.datetime.now()
        self.assertEquals(req.method, "GET")
        self.assertEquals(req.url, "/test/me/")
        self.assertEquals(req.date.date(), now.date())
        self.assertEquals(req.date.hour, now.hour)
        self.assertEquals(req.date.minute, now.minute)
        self.assertTrue((now.second - req.date.second) <= 1)
