from tddspry.django.cases import HttpTestCase


class WebTest(HttpTestCase):
    start_live_server = 1

    def test_bio_index(self):
        self.go200("/")
        self.title("My biography")
        self.find("Igor")
        self.find("Tonky")
        self.find("Born and alive")
        self.find("igor.tonky@gmail.com")
