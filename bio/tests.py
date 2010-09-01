import datetime
import time
from twill.commands import notfind, find, code, title, go, fv, submit, url, follow
from twill.commands import showforms
from tddspry import NoseTestCase
from django.test.client import Client
from django.forms import ModelForm
import settings
from bio.models import Log, Bio
from django.contrib.auth.models import User, check_password
from bio.views import BioForm


class WebTest(NoseTestCase):
    start_live_server = True

    def test_form_inversion(self):
        class StraightBioForm(ModelForm):

            class Meta:
                model = Bio

        old_order = StraightBioForm.base_fields.keys()
        new_order = BioForm.base_fields.keys()

        self.assertEquals(list(reversed(old_order)), new_order)


    def test_bio_index(self):
        go("http://localhost:8000/")
        title("My biography")
        find("Igor")
        find("Tonky")
        find("Born and alive")
        find("igor.tonky@gmail.com")

    def test_edit_require_auth(self):
        go("http://localhost:8000/edit/")

        find("Please log in:")
        url("http://localhost:8000/login/")

    def test_not_logged_in(self):
        go("http://localhost:8000/logout/")
        url("http://localhost:8000/")
        find("Login to edit it")
        notfind("Logout")
        notfind("Edit bio")

    def test_logout(self):
        go("http://localhost:8000/login/")

        fv("1", "username", "tonky")
        fv("1", "password", "1")
        showforms()
        submit('0')

        go("http://localhost:8000/logout/")

        url("http://localhost:8000/")
        find("Login to edit it")
        notfind("Logout")
        notfind("Edit bio")

    def test_logged_in(self):
        go("http://localhost:8000/login/")

        fv("1", "username", "tonky")
        fv("1", "password", "1")
        submit('0')

        url("http://localhost:8000/")
        notfind("Login")
        find("logout")
        find("Edit this data")

    def test_edit_form_error(self):
        go("http://localhost:8000/login/")

        fv("1", "username", "tonky")
        fv("1", "password", "1")
        submit('0')

        go("http://localhost:8000/edit/")
        fv("1", "name", "")
        submit('0')

        url("http://localhost:8000/save/")
        find("Tonky")
        notfind("Igor")
        find("Name is required and should be valid.")

    def test_edit_form_saved(self):
        go("http://localhost:8000/login/")

        fv("1", "username", "tonky")
        fv("1", "password", "1")
        submit('0')

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
        self.assertEquals(response.context['settings'].DATABASES, settings.DATABASES)
