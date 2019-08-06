from unittest import TestCase
from django.conf import settings
from importlib import import_module
from django.test import RequestFactory, SimpleTestCase, Client
from django.urls import reverse, resolve
from mixer.auto import mixer
from Algoritma.views import *

class SessionTestCase(TestCase):
    def setUp(self):
        # http://code.djangoproject.com/ticket/10899
        settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store
        self.client = Client()
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

class TestViews(SessionTestCase):
    # def test_signin_already_authenticated(self):
    #     session = self.session
    #     session['uid'] = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjcyODRlYTZiNGZlZDBmZDc1MzE4NTg2NDZmZDYzNjE1ZGQ3YTIyZjUiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vaW5ub3NvZnQtZGphbmdvIiwiYXVkIjoiaW5ub3NvZnQtZGphbmdvIiwiYXV0aF90aW1lIjoxNTY1MDM4MjYwLCJ1c2VyX2lkIjoickxGckFHcXdyV01zb21HVEtwMWNhY0xJckNGMyIsInN1YiI6InJMRnJBR3F3cldNc29tR1RLcDFjYWNMSXJDRjMiLCJpYXQiOjE1NjUwMzgyNjAsImV4cCI6MTU2NTA0MTg2MCwiZW1haWwiOiJhc2thckBlbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsiZW1haWwiOlsiYXNrYXJAZW1haWwuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoicGFzc3dvcmQifX0.ZfbfZpxaYZfOyvj8326D11lZ0flSQ10-EDJ1hrJ6Lr_rMtwwyLgzhVa7SU8K56bW-1RKw_Y9_ay8aSBG6mY9N5e63DVlv84RtEtx1FoPnSvr7booNh7PbWMTLw2_13n0nr5hYaelwIfnfyyhzfNwbh0XKdlfq0fh7AyrHu5XssztURfO_lkmhtMnZiCtVwnXSVuqYiVAFxmwe4EY_dcgeYOgZO82YyKgKCWTWhP8kCY02yAYHCNOES8iqln3c7yrJ8R-QKGB58pi_cs8ZGX-WlGMhTG9UA1bfVS_jywTrEhsCqCfrEBW8CLZxQm8UW_6TUH-jMW1AJYH8IN9lseW8Q'
    #     session.save()
    #     response = self.client.get(reverse('signin'), follow=True)
    #     SimpleTestCase().assertRedirects(response, reverse('user_project_index'))

    def test_signin_right_cred(self):
        response = self.client.post(reverse('signin'), {'email': 'askar@email.com', 'password': 'dsadmin'}, follow=True)
        SimpleTestCase().assertRedirects(response, reverse('user_project_index'))

    # def test_signup_already_authenticated(self):
    #     session = self.session
    #     session['uid'] = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjcyODRlYTZiNGZlZDBmZDc1MzE4NTg2NDZmZDYzNjE1ZGQ3YTIyZjUiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vaW5ub3NvZnQtZGphbmdvIiwiYXVkIjoiaW5ub3NvZnQtZGphbmdvIiwiYXV0aF90aW1lIjoxNTY1MDM4MjYwLCJ1c2VyX2lkIjoickxGckFHcXdyV01zb21HVEtwMWNhY0xJckNGMyIsInN1YiI6InJMRnJBR3F3cldNc29tR1RLcDFjYWNMSXJDRjMiLCJpYXQiOjE1NjUwMzgyNjAsImV4cCI6MTU2NTA0MTg2MCwiZW1haWwiOiJhc2thckBlbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsiZW1haWwiOlsiYXNrYXJAZW1haWwuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoicGFzc3dvcmQifX0.ZfbfZpxaYZfOyvj8326D11lZ0flSQ10-EDJ1hrJ6Lr_rMtwwyLgzhVa7SU8K56bW-1RKw_Y9_ay8aSBG6mY9N5e63DVlv84RtEtx1FoPnSvr7booNh7PbWMTLw2_13n0nr5hYaelwIfnfyyhzfNwbh0XKdlfq0fh7AyrHu5XssztURfO_lkmhtMnZiCtVwnXSVuqYiVAFxmwe4EY_dcgeYOgZO82YyKgKCWTWhP8kCY02yAYHCNOES8iqln3c7yrJ8R-QKGB58pi_cs8ZGX-WlGMhTG9UA1bfVS_jywTrEhsCqCfrEBW8CLZxQm8UW_6TUH-jMW1AJYH8IN9lseW8Q'
    #     session.save()
    #     response = self.client.get(reverse('signup'), follow=True)
    #     SimpleTestCase().assertRedirects(response, reverse('user_project_index'))
