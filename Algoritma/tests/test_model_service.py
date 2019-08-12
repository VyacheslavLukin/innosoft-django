from datetime import datetime
from unittest import TestCase

from Algoritma.services.model_service import ModelService
from Algoritma.services.user_service import UserService
from Algoritma.tests.test_base import AlgoritmaTestCase


class TestModelService(AlgoritmaTestCase):

    def __init__(self, method_name='runTest'):
        super().__init__(method_name)
        self.user_service = ModelService.get_instance()
        self.user_service = UserService.get_instance()

    def test_create_model(self):
        pass