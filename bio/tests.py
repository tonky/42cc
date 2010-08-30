import time, datetime

from tddspry.django import HttpTestCase

from mybio import settings

from selenium.remote import connect
from selenium import FIREFOX

from mybio.bio.models import Log, Bio

class WebTest(HttpTestCase):
    start_live_server = True

    def setUp(self):
        self.browser = connect(FIREFOX)
        self.by_id = self.browser.find_element_by_id

        a = Log.objects.all()
        from django.db import connection
        # print settings.DATABASES
        # print dir(connection)
        # print connection.connection
        # print connection.introspection
        # print connection.settings_dict

    def test_bio_index(self):
        # self.go('/')
        self.browser.get("http://localhost:8000/")

        # print self.browser.get_page_source()

        self.assertEquals(self.browser.get_title(), "My biography")
        self.assertEquals(self.by_id("name").get_text(), "Igor")
        self.assertEquals(self.by_id("surname").get_text(), "Tonky")
        self.assertEquals(self.by_id("bio").get_text(), "Born and alive")
        self.assertEquals(self.by_id("email").get_text(), "igor.tonky@gmail.com")

    def test_middleware_logging(self):
        self.browser.get("http://localhost:8000/test/me/")
        last_two = Log.objects.order_by('-date')[:2] # by date
        req = last_two[1] # firefox asks for favicon after the initial request

        now = datetime.datetime.now()
        self.assertEquals(req.method, "GET")
        self.assertEquals(req.url, "/test/me/")
        self.assertEquals(req.date.date(), now.date())
        self.assertEquals(req.date.hour, now.hour)
        self.assertEquals(req.date.minute, now.minute)
        self.assertTrue((now.second - req.date.second) <= 1)

    def tearDown(self):
        self.browser.close()
