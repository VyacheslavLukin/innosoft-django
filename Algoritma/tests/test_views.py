from unittest import TestCase

from django.test import RequestFactory, SimpleTestCase, Client
from django.urls import reverse, resolve
from mixer.auto import mixer
from Algoritma.views import *

class TestViews(TestCase):
    def test_signin_is_not_authenticated(self):
        client = Client()
        response = client.get(reverse('signin'), {'uid': 'rLFrAGqwrWMsomGTKp1cacLIrCF3'}, follow=True)
        SimpleTestCase.assertRedirects(response, reverse('user_project_index'))
