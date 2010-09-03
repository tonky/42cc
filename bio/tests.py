import datetime
import os
import time
from subprocess import Popen, PIPE
import unittest
from tddspry.django import HttpTestCase, DatabaseTestCase
from django.test.client import Client
from django.forms import ModelForm
import settings
from bio.models import Log, Bio, CrudLog
from bio.views import BioForm

from selenium.remote import connect
from selenium import FIREFOX


class CommandTest(unittest.TestCase):

    def testAllModels(self):
        p = Popen(["python", os.path.join(os.getcwd(), "manage.py"), "models"],
                stdout=PIPE)

        models = p.stdout.readlines()

        expected = ["Bio: 1\n", "Log: 0\n", "CrudLog: 49\n"]  # after fixture

        self.assertEquals(models, expected)


class DbTest(DatabaseTestCase):

    def test_create(self):
        self.assert_create(Bio, name="Bender", born="2980-01-01")

        req = CrudLog.objects.order_by("-date")[0]

        self.assert_equals(req.action, "create")
        self.assert_equals(req.model, "Bio")

    def test_update(self):
        bio = self.assert_create(Bio, name="Bender", born="2980-01-01")
        self.assert_update(bio, name="Flex-o")

        req = CrudLog.objects.order_by("-date")[0]

        self.assert_equals(req.action, "update")
        self.assert_equals(req.model, "Bio")

    def test_delete(self):
        bio = self.assert_create(Bio, name="Bender", born="2980-01-01")
        self.assert_delete(bio)

        req = CrudLog.objects.order_by("-date")[0]

        self.assert_equals(req.action, "delete")
        self.assert_equals(req.model, "Bio")


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


class JsTest(HttpTestCase):
    start_live_server = True

    def setUp(self):
        self.b = connect(FIREFOX)

    def _login(self):
        self.b.get("http://localhost:8000/login/")
        self.b.find_element_by_id("id_username").send_keys("tonky")
        self.b.find_element_by_id("id_password").send_keys("1")
        self.b.find_element_by_id("login").submit()

    def test_ajax_submit_form(self):
        self._login()

        self.b.find_element_by_id("id_name").send_keys("elvis")

        ajax_submit = self.b.find_element_by_name("save_bio_ajax")
        ajax_submit.click()

        self.b.find_element_by_name("save_bio_ajax").click()

        self.assertEquals(self.b.get_current_url(), "http://localhost:8000/")
        self.assertEquals(self.b.find_element_by_id("name").get_text(), "elvis")

    def test_ajax_submit_form_error(self):
        self._login()

        self.b.find_element_by_id("id_name").send_keys("elvis")

        ajax_submit = self.b.find_element_by_name("save_bio_ajax")
        ajax_submit.click()

        self.b.find_element_by_name("save_bio_ajax").click()

        self.assertRaises(self.b.find_element_by_name("save_bio_ajax"),
                NotFound)

        s = self.b.find_element_by_id("id_surname").get_attribute("readonly")
        self.assertEquals(s, "readonly")

        err = self.b.find_element_by_id("errors").get_text()

        name_err = "Name is required and should be valid."

        self.assertEquals(err, name_err)

    def test_datepicker_select(self):
        self.b.get("http://localhost:8000/login/")
        self.b.find_element_by_id("id_username").send_keys("tonky")
        self.b.find_element_by_id("id_password").send_keys("1")
        self.b.find_element_by_id("login").submit()

        self.b.get("http://localhost:8000/edit/")
        self.assertEquals(self.b.get_current_url(), "http://localhost:8000/edit/")

        self.b.find_element_by_id("id_born").click()
        self.b.find_element_by_link_text("15").click()
        self.assertEquals(self.b.find_element_by_id("id_born").get_value(), "1981-01-15")
        self.b.find_element_by_name("save_bio").click()

        self.assertEquals(self.b.get_current_url(), "http://localhost:8000/")
        self.assertEquals(self.b.find_element_by_id("born").get_text(), "Jan. 15, 1981")

    def tearDown(self):
        self.b.close()
