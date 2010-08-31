from tddspry import NoseTestCase

from twill.commands import find, code, title, go

class WebTest(NoseTestCase):
    start_live_server = 1
    
    def test_bio_index(self):
        go("http://localhost:8000/")
        title("My biography")
        find("Igor")
        find("Tonky")
        find("Born and alive")
        find("igor.tonky@gmail.com")
