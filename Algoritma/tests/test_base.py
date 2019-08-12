from datetime import datetime
from unittest import TestCase
from django.conf import settings
from importlib import import_module
from django.test import RequestFactory, SimpleTestCase, Client
import os


class AlgoritmaTestCase(TestCase):
    def __init__(self, method_name='runTest'):
        super().__init__(method_name)
        os.environ['DJANGO_SETTINGS_MODULE'] = 'Algoritma.settings'
        settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store
        self.client = Client()

    def generate_name(self):
        ts = datetime.now()
        tstr = ts.strftime('%Y%m%d%H%M%S')
        return tstr

    def generate_cred_base(self):
        name = 'test%s' % self.generate_name()
        email = '%s@email.com' % (name)
        password = '%spass' % (name)
        info = {'name': name, 'email': email, 'password': password, 'image': None}
        return info

    def generate_cred_ds(self):
        info = self.generate_cred_base()
        info['role'] = 'ds'
        info['account_type'] = 'ds'
        return info

    def generate_cred_org(self):
        info = self.generate_cred_base()
        info['role'] = 'org'
        info['account_type'] = 'org'
        return info
