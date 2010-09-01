from tddspry import NoseTestCase
import settings
from django.test.client import Client


class WebTest(NoseTestCase):
    start_live_server = True

    def test_context_settings(self):
        c = Client()
        response = c.get('/')
        self.assertEquals(response.context['settings'], settings)
