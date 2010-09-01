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

    def test_edit_require_auth(self):
        self.go("/edit/")

        self.find("Please log in:")
        self.url('/login/.*')

    def test_not_logged_in(self):
        self.go200("/logout/")
        self.url("/")
        self.find("Login to edit it")
        self.notfind("Logout")
        self.notfind("Edit bio")

    def test_logout(self):
        self.go200("/login/")

        self.fv("1", "username", "tonky")
        self.fv("1", "password", "1")
        self.submit('0')

        self.go200("/logout/")

        self.url("/")
        self.find("Login to edit it")
        self.notfind("Logout")
        self.notfind("Edit bio")

    def test_logged_in(self):
        self.go200("/login/")

        self.fv("1", "username", "tonky")
        self.fv("1", "password", "1")
        self.submit('0')

        self.url("/")
        self.notfind("Login")
        self.find("logout")
        self.find("Edit this data")

    def test_edit_form_error(self):
        self.go200("/login/")

        self.fv("1", "username", "tonky")
        self.fv("1", "password", "1")
        self.submit('0')

        self.go200("/edit/")
        self.fv("1", "name", "")
        self.submit('0')

        self.url("/save/")
        self.find("Tonky")
        self.notfind("Igor")
        self.find("Name is required and should be valid.")

    def test_edit_form_saved(self):
        self.go200("/login/")

        self.fv("1", "username", "tonky")
        self.fv("1", "password", "1")
        self.submit('0')

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
        self.assertEquals(response.context['settings'].DATABASES, settings.DATABASES)
