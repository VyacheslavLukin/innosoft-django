from datetime import datetime
from unittest import TestCase

from django.test import SimpleTestCase
from django.urls import reverse

from Algoritma.services.user_service import UserService
from Algoritma.tests.test_base import AlgoritmaTestCase


class TestUserService(AlgoritmaTestCase):

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.user_service = UserService.getInstance()

    def test_signin_right_cred(self):
        email = 'askar@email.com'
        password = 'dsadmin'
        user = self.user_service.signin(email, password)
        self.assertIsNotNone(user)

    def test_signin_wrong_pass(self):
        email = 'askar@email.com'
        password = 'wrong'
        user = self.user_service.signin(email, password)
        self.assertIsNone(user)

    def test_signin_email_not_exist(self):
        email = 'wrong@email.com'
        password = 'wrong'
        user = self.user_service.signin(email, password)
        self.assertIsNotNone(user)

    def test_create_account_ds_no_image(self):
        name = 'test%s' % self.generate_name()
        email = '%s@email.com' % (name)
        password = '%spass' % (name)
        info = {'name': name, 'email': email, 'password': password, 'role': 'ds', 'image': None}
        user = self.user_service.create_account(info)
        self.assertIsNotNone(user)
        print(name)
        self.user_service.remove_account(email, password)

    def test_create_account_org_no_image(self):
        name = 'test%s' % self.generate_name()
        email = '%s@email.com' % (name)
        password = '%spass' % (name)
        info = {'name': name, 'email': email, 'password': password, 'role': 'org', 'image': None}
        user = self.user_service.create_account(info)
        self.assertIsNotNone(user)
        self.user_service.remove_account(email, password)

    def test_user_by_email_right_cred(self):
        name = 'test%s' % self.generate_name()
        email = '%s@email.com' % (name)
        password = '%spass' % (name)
        info = {'name': name, 'email': email, 'password': password, 'role': 'org', 'image': None}
        check_user = self.user_service.create_account(info)
        user = self.user_service.get_user_by_email(email)
        self.assertTrue(user and user.get('email') == check_user.get('email'))
        self.user_service.remove_account(email, password)

    def test_remove_user(self):
        name = 'test%s' % self.generate_name()
        email = '%s@email.com' % (name)
        password = '%spass' % (name)
        info = {'name': name, 'email': email, 'password': password, 'role': 'org', 'image': None}
        user = self.user_service.create_account(info)
        self.user_service.remove_account(email, password)
        self.assertTrue(True)

    def test_remove_testing_users(self):
        users = self.user_service.get_users_list('test')
        for user in users:
            name = user.get('name')
            email = '%s@email.com' % name
            password = '%spass' % name
            print(name, email, password)
            self.user_service.remove_account(email, password)
