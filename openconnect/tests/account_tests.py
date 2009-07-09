from django.test.client import Client
from django.test import TestCase

class TestAccounts(TestCase):
    fixtures = ['tests/login.json']

    def test_login(self):
        c = Client()
        assert c.login(username='john', password='abc123') == True


