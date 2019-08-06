from unittest import TestCase

from Algoritma.services.project_service import ProjectService
from Algoritma.tests.test_base import AlgoritmaTestCase


class TestProjectService(AlgoritmaTestCase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.project_service = ProjectService.getInstance()

    def test_get_market_projects(self):
        projects = self.project_service.get_market_projects()
        flag = True
        if len(projects) > 0:
            for project in projects:
                flag = project.get('type') == 'market'
        self.assertTrue(flag)
