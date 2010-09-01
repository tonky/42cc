import time, datetime
from twill.commands import notfind, find, code, title, go, fv, submit, url, follow
from tddspry import NoseTestCase
from django.test.client import Client
import settings
from bio.models import Log, Bio


class WebTest(NoseTestCase):
    start_live_server = True

    def test_bio_index(self):
        go("http://localhost:8000/")
        title("My biography")
        find("Igor")
        find("Tonky")
        find("Born and alive")
        find("igor.tonky@gmail.com")

    def test_edit_form_error(self):
        go("http://localhost:8000/edit/")
        fv("1", "name", "")
        submit('0')

        url("http://localhost:8000/save/")
        find("Tonky")
        notfind("Igor")
        find("Name is required and should be valid.")

    def test_edit_form_saved(self):
        go("http://localhost:8000/edit/")
        fv("1", "name", "HYPNOTOAD")
        fv("1", "email", "omicron@persei.no9")
        submit('0')

        url("http://localhost:8000/")
        find("HYPNOTOAD")
        find("omicron@persei.no9")

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

    def test_context_settings(self):
        c = Client()
        response = c.get('/')
        self.assertEquals(response.context['settings'], settings)
