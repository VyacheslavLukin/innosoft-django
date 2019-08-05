from unittest import TestCase

import pytest
from django.urls import reverse, resolve

class TestUrls(TestCase):
    def test_signin_url(self):
        path = reverse('signin')
        assert resolve(path).view_name == 'signin'

    def test_signup_url(self):
        path = reverse('signup')
        assert resolve(path).view_name == 'signup'

    def test_signout_url(self):
        path = reverse('signout')
        assert resolve(path).view_name == 'signout'

    def test_market_project_index_url(self):
        path = reverse('market_project_index')
        assert resolve(path).view_name == 'market_project_index'

    def test_user_project_index_url(self):
        path = reverse('user_project_index')
        assert resolve(path).view_name == 'user_project_index'

    def test_create_market_project_url(self):
        path = reverse('create_market_project')
        assert resolve(path).view_name == 'create_market_project'

    def test_create_custom_project_url(self):
        path = reverse('create_custom_project')
        assert resolve(path).view_name == 'create_custom_project'

    def test_market_project_page_url(self):
        path = reverse('market_project_page', kwargs={'prj_id': '-Lg1231a2'} )
        assert resolve(path).view_name == 'market_project_page'

    def test_custom_project_page_url(self):
        path = reverse('custom_project_page', kwargs={'prj_id': '-Lg1231a2'})
        assert resolve(path).view_name == 'custom_project_page'

    def test_join_market_project_url(self):
        path = reverse('join_market_project', kwargs={'prj_id': '-Lg1231a2'})
        assert resolve(path).view_name == 'join_market_project'

    def test_invite_user_url(self):
        path = reverse('invite_user')
        assert resolve(path).view_name == 'invite_user'

    def test_model_index_url(self):
        path = reverse('model_index')
        assert resolve(path).view_name == 'model_index'

    def test_upload_model_url(self):
        path = reverse('upload_model')
        assert resolve(path).view_name == 'upload_model'