import datetime
import time
from tddspry.django import HttpTestCase
from django.test.client import Client
import settings
from bio.models import Log, Bio


class WebTest(HttpTestCase):
    start_live_server = True

    def test_bio_index(self):
        self.go200("/")
        self.title("My biography")
        self.find("Igor")
        self.find("Tonky")
        self.find("Born and alive")
        self.find("igor.tonky@gmail.com")

    def test_edit_form_error(self):
        self.go("/edit/")
        self.fv("1", "name", "")
        self.submit('0')

        self.url("/save/")
        self.find("Tonky")
        self.notfind("Igor")
        self.find("Name is required and should be valid.")

    def test_edit_form_saved(self):
        self.go("/edit/")
        self.fv("1", "name", "HYPNOTOAD")
        self.fv("1", "email", "omicron@persei.nine")
        self.submit('0')

        self.url("/")
        self.find("HYPNOTOAD")
        self.find("omicron@persei.nine")

    def test_middleware_logging(self):
        self.go("/test/me/")

        req = Log.objects.order_by('-date')[0] # last by date

        now = datetime.datetime.now()
        self.assertEquals(req.method, "GET")
        self.assertEquals(req.url, "/test/me/")
        self.assertEquals(req.date.date(), now.date())
        self.assertEquals(req.date.hour, now.hour)
        self.assertEquals(req.date.minute, now.minute)
        self.assertTrue((now.second - req.date.second) <= 1)

    def test_context_settings(self):
        c = Client()
        response = c.get('/')
        self.assertEquals(response.context['settings'], settings)
