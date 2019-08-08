from datetime import datetime
from unittest import TestCase

from Algoritma.services.model_service import ModelService
from Algoritma.services.user_service import UserService
from Algoritma.tests.test_base import AlgoritmaTestCase


class TestModelService(AlgoritmaTestCase):

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.user_service = ModelService.getInstance()
        self.user_service = UserService.getInstance()

    def test_create_model(self):
        pass