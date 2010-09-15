import datetime
import json
import os
import re
import time
from subprocess import Popen, PIPE
from tddspry.django import HttpTestCase, DatabaseTestCase
from django.forms import ModelForm
from django.test.client import Client
from django.test import TestCase
import settings
from bio.management.commands.models import objects_count
from bio.models import Log, Bio, CrudLog
from bio.views import BioForm
from bio.management.commands.models import objects_count


from selenium.remote import connect
from selenium import FIREFOX
from selenium.common.exceptions import ElementNotVisibleException


class CommandTest(TestCase):

    def testAllModels(self):
        p = Popen(["python", os.path.join(os.getcwd(), "manage.py"), "models"],
                stdout=PIPE)

        models = p.stdout.read()

        # make sure it works at all
        models_regexp = 'Bio: \d+\nLog: \d+\nCrudLog: \d+\n'
        match_err = "\n%s==== got ====\n%s" % (models_regexp, models)

        self.assertTrue(re.match(models_regexp, models), match_err)

        expected = [("Bio", 1), ("Log", 0), ("CrudLog", 47)]  # after fixtures

        # make sure it reads correct data from db
        self.assertEquals(expected, objects_count([Bio, Log, CrudLog]))


class DbTest(DatabaseTestCase):

    def test_create(self):
        self.assert_create(Bio, first_name="Bender", born="2980-01-01")

        req = CrudLog.objects.order_by("-date")[0]

        self.assert_equals(req.action, "create")
        self.assert_equals(req.model, "Bio")

    def test_update(self):
        bio = self.assert_create(Bio, first_name="Bender", born="2980-01-01")
        self.assert_update(bio, first_name="Flex-o")

        req = CrudLog.objects.order_by("-date")[0]

        self.assert_equals(req.action, "update")
        self.assert_equals(req.model, "Bio")

    def test_delete(self):
        bio = self.assert_create(Bio, first_name="Bender", born="2980-01-01")
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
        self.submit200('login')

        self.go200("/logout/")

        self.url("/")
        self.find("Login to edit it")
        self.notfind("Logout")
        self.notfind("Edit bio")

    def test_logged_in(self):
        self.go200("/login/")

        self.fv("1", "username", "tonky")
        self.fv("1", "password", "1")
        self.submit200('login')

        self.url("/")
        self.notfind("Login")
        self.find("logout")
        self.find("Edit this data")

    def test_edit_form_error(self):
        self.go200("/login/")

        self.fv("1", "username", "tonky")
        self.fv("1", "password", "1")
        self.submit200('login')

        self.go200("/edit/")
        self.fv("2", "first_name", "")
        self.submit200('save_bio')

        self.url("/save/")
        self.find("Tonky")
        self.notfind("Igor")
        self.find("First_name is required and should be valid.")

    def test_edit_form_error_ajax(self):
        self.go200("/login/")

        self.fv(1, "username", "tonky")
        self.fv(1, "password", "1")
        self.submit200('login')

        self.go200("/edit/")

        self.fv(2, "first_name", "")
        self.fa(2, 'http://localhost:8000/save_ajax/')

        # required to bypass csrf check
        self.add_extra_header("X-Requested-With", "XMLHttpRequest")

        self.submit200("save_bio")

        resp = json.loads(self.show())

        self.assertEquals(resp['status'], 1)
        self.assertEquals(resp['errors'],
                          {u"first_name": [u"This field is required."]})

    def test_edit_form_ajax_saved(self):
        self.go200("/login/")

        self.fv(1, "username", "tonky")
        self.fv(1, "password", "1")
        self.submit200('login')

        self.go200("/edit/")

        self.fv(2, "first_name", "Nibbler")
        self.fa(2, 'http://localhost:8000/save_ajax/')

        # required to bypass csrf check
        self.add_extra_header("X-Requested-With", "XMLHttpRequest")

        self.submit200("save_bio")

        resp = json.loads(self.show())

        self.assertEquals(resp['status'], 0)

        self.go200("/")
        self.find("Nibbler")

    def test_edit_form_saved(self):
        self.go200("/login/")

        self.fv("1", "username", "tonky")
        self.fv("1", "password", "1")
        self.submit200("login")

        self.go200("/edit/")
        self.fv("2", "first_name", "HYPNOTOAD")
        self.fv("2", "email", "omicron@persei.nine")
        self.submit200("save_bio")

        self.url("/")
        self.find("HYPNOTOAD")
        self.find("omicron@persei.nine")

    def test_middleware_logging(self):
        self.go("/test/me/")

        req = Log.objects.order_by('-date')[0]  # last by date

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
        self.assertEquals(response.context['settings'].DATABASES,
                          settings.DATABASES)

    def test_template_tag(self):
        self.go200("/")
        links = [l.url for l in self.showlinks()]

        self.assertTrue("/login/" in links)
        self.assertTrue("/admin/bio/bio/1/" in links)
        self.assertFalse("/admin/auth/user/1/" in links)

        self.go200("/login/")

        self.fv("1", "username", "tonky")
        self.fv("1", "password", "1")
        self.submit200('login')

        links = [l.url for l in self.showlinks()]

        self.assertTrue("/admin/auth/user/1/" in links)

    def test_first_ten_requests(self):
        self.go200("/")
        self.go200("/")
        self.go200("/")
        self.go200("/")
        self.go200("/")
        self.go200("/login/")
        self.go200("/login/")
        self.go200("/login/")
        self.go200("/login/")
        self.go200("/login/")
        self.go200("/logout/")
        self.go200("/first10/")

        self.find("\[GET\] \/")
        self.find("\[GET\] \/login\/")
        self.notfind("\[GET\] \/logout\/")
        self.notfind("\[GET\] \/first10\/")
