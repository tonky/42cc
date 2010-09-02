import datetime
import time
from tddspry.django import HttpTestCase
from django.test.client import Client
from django.forms import ModelForm
import settings
from bio.models import Log, Bio
from bio.views import BioForm

from selenium.remote import connect
from selenium import FIREFOX


class WebTest(HttpTestCase):
    start_live_server = True

    def test_form_inversion(self):

        class StraightBioForm(ModelForm):

            class Meta:
                model = Bio

        old_order = StraightBioForm.base_fields.keys()
        new_order = BioForm.base_fields.keys()


        self.assertEquals(list(reversed(old_order)), new_order)

    def test_bio_index(self):
        self.go200("/")
        self.title("My biography")
        self.find("Igor")
        self.find("Tonky")
        self.find("Born and alive")
        self.find("igor.tonky@gmail.com")

    def test_edit_require_auth(self):
        self.go200("/edit/")

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

        self.go200("/edit/")
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

    def test_template_tag(self):
        self.go200("/")
        links = [l.url for l in self.showlinks()]

        self.assertTrue("/login/" in links)
        self.assertTrue("/admin/bio/bio/1/" in links)
        self.assertFalse("/admin/auth/user/1/" in links)

        self.go200("/login/")

        self.fv("1", "username", "tonky")
        self.fv("1", "password", "1")
        self.submit('0')

        links = [l.url for l in self.showlinks()]

        self.assertTrue("/admin/auth/user/1/" in links)

    def test_datepicker_select(self):
        b = connect(FIREFOX)

        b.get("http://localhost:8000/login/")
        b.find_element_by_id("id_username").send_keys("tonky")
        b.find_element_by_id("id_password").send_keys("1")
        b.find_element_by_id("login").submit()

        b.get("http://localhost:8000/edit/")
        self.assertEquals(b.get_current_url(), "http://localhost:8000/edit/")

        b.find_element_by_id("id_born").click()
        b.find_element_by_link_text("15").click()
        self.assertEquals(b.find_element_by_id("id_born").get_value(), "1981-01-15")
        b.find_element_by_name("save_bio").click()

        self.assertEquals(b.get_current_url(), "http://localhost:8000/")
        self.assertEquals(b.find_element_by_id("born").get_text(), "Jan. 15, 1981")

        b.close()
