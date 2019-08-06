from django.test import RequestFactory, SimpleTestCase, Client
from django.urls import reverse, resolve

from Algoritma.tests.test_base import AlgoritmaTestCase
from Algoritma.views import *

class TestViews(AlgoritmaTestCase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.user_service = UserService.getInstance()
        import django
        django.setup()

    def generate_project_cred(self):
        name = self.generate_name()
        #register new user
        info = {}
        info['title'] = 'title %s' % name
        info['short_desc'] = 'short_desc %s' % name
        info['description'] = 'description %s' % name
        info['percentage'] = 80
        info['start_date'] = '2019-08-01'
        info['end_date'] = '2019-09-01'
        info['eval_rules'] = 'Min absolute error'
        info['rules'] = 'rules %s' % name
        info['prizes'] = 'prizes %s' % name
        info['req_cols'] = ['snow_intensity']
        info['opt_cols'] = ['rain_intensity']
        return info

    def test_signin_not_authenticated(self):
        response = self.client.get('/signin/')
        SimpleTestCase().assertEqual(response.status_code, 200)

    def test_signin_already_authenticated(self):
        info = self.generate_cred_ds()
        user = self.user_service.create_account(info)
        email = info.get('email')
        password = info.get('password')
        signin_user = self.user_service.signin(email, password)
        session = self.client.session
        session['uid'] = signin_user.get('idToken')
        session.save()
        response = self.client.get(reverse('signin'), follow=True)
        SimpleTestCase().assertRedirects(response, reverse('user_project_index'))

    def test_signin_right_cred(self):
        response = self.client.post(reverse('signin'), {'email': 'askar@email.com', 'password': 'dsadmin'}, follow=True)
        SimpleTestCase().assertRedirects(response, reverse('user_project_index'))

    def test_signin_wrong_cred(self):
        response = self.client.post(reverse('signin'), {'email': 'askar@email.com', 'password': 'wrong'}, follow=True)
        self.assertIsNotNone(response.context.get('message'))

    def test_signup_already_authenticated(self):
        info = self.generate_cred_ds()
        user = self.user_service.create_account(info)
        email = info.get('email')
        password = info.get('password')
        user = self.user_service.create_account(info)
        signin_user = self.user_service.signin(email, password)
        session = self.client.session
        session['uid'] = signin_user.get('idToken')
        session.save()
        response = self.client.get(reverse('signup'), follow=True)
        SimpleTestCase().assertRedirects(response, reverse('user_project_index'))

    def test_signout(self):
        response = self.client.get(reverse('signout'))
        SimpleTestCase().assertRedirects(response, reverse('signin'))

    def test_signup_right_cred(self):
        info = self.generate_cred_ds()
        response = self.client.post(reverse('signup'), info, follow=True)
        SimpleTestCase().assertRedirects(response, reverse('signin'))

    def test_create_market_project(self):
        user_info = self.generate_cred_org()
        email = user_info.get('email')
        password = user_info.get('password')
        user = self.user_service.create_account(user_info)
        signin_user = self.user_service.signin(email, password)
        session = self.client.session
        session['uid'] = signin_user.get('idToken')
        session.save()
        project_info = self.generate_project_cred()
        with open('test_ds.json') as file:
            project_info['file'] = file
            response = self.client.post(reverse('create_market_project'), project_info)
            SimpleTestCase().assertRedirects(response, reverse('market_project_index'))

    def test_create_custom_project(self):
        user_info = self.generate_cred_ds()
        email = user_info.get('email')
        password = user_info.get('password')
        user = self.user_service.create_account(user_info)
        signin_user = self.user_service.signin(email, password)
        session = self.client.session
        session['uid'] = signin_user.get('idToken')
        session.save()
        project_info = self.generate_project_cred()
        with open('test_ds.json') as file:
            project_info['file'] = file
            response = self.client.post(reverse('create_custom_project'), project_info)
            SimpleTestCase().assertRedirects(response, reverse('user_project_index'))

    def test_upload_model(self):
        user_info = self.generate_cred_ds()
        email = user_info.get('email')
        password = user_info.get('password')
        user = self.user_service.create_account(user_info)
        signin_user = self.user_service.signin(email, password)
        session = self.client.session
        session['uid'] = signin_user.get('idToken')
        session.save()
        model_info = {'name ': 'model %s' % self.generate_name()}
        with open('test_model.pickle') as file:
            model_info['file'] = file
            response = self.client.post(reverse('upload_model'), model_info)
            SimpleTestCase().assertRedirects(response, reverse('upload_model'))

    def test_market_project_page_get(self):
        user_info = self.generate_cred_org()
        email = user_info.get('email')
        password = user_info.get('password')
        user = self.user_service.create_account(user_info)
        signin_user = self.user_service.signin(email, password)
        session = self.client.session
        session['uid'] = signin_user.get('idToken')
        session.save()
        project_info = self.generate_project_cred()
        with open('test_ds.json') as file:
            project_info['file'] = file
            response = self.client.post(reverse('create_market_project'), project_info)

