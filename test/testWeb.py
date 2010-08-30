import unittest, time, re

from selenium.remote import connect
from selenium import FIREFOX

from mybio.bio.models import MwareRequest

class WebTest(unittest.TestCase):
    def setUp(self):
        self.browser = connect(FIREFOX)
        self.by_id = self.browser.find_element_by_id

    def test_bio_index(self):
        self.browser.get("http://localhost:8000/")
        self.assertEquals(self.browser.get_title(), "My biography")
        self.assertEquals(self.by_id("name").get_text(), "Igor")
        self.assertEquals(self.by_id("surname").get_text(), "Tonky")
        self.assertEquals(self.by_id("bio").get_text(), "Born and alive")
        self.assertEquals(self.by_id("email").get_text(), "igor.tonky@gmail.com")

    def test_bio_index(self):
        self.browser.get("http://localhost:8000/test/me/")
        req = MwareRequest.objects.order_by('-date')[0]

        self.assertEquals(req.url, "/test/me/")
        self.assertTrue(req.date, time.time())

    def tearDown(self):
        self.browser.close()


if __name__ == '__main__':
    unittest.main()
