from Algoritma.services.db_servise import FirebaseService
from Algoritma.services.file_service import FileService
from Algoritma.services.model_service import ModelService

class ProjectService:
    __instance = None

    @classmethod
    def get_instance(self):
        if not self.__instance:
            self.__instance = ProjectService()
        return self.__instance

    def __init__(self):
        self.db = FirebaseService.get_instance()
        self.file_service = FileService.get_instance()
        self.model_service = ModelService.get_instance()

    def get_market_projects(self):
        prj_keys = self.db.firedb.child('projects').child('market').shallow().get().val()

        projects = []
        if prj_keys:
            for key in prj_keys:
                project = self.get_project(key)
                projects.append(dict(project))

        return projects

    MARKET_PROJECT = 'market'
    CUSTOM_PROJECT = 'custom'

    def create_market_project(self, info: dict):
        user = info['user']
        info.pop('user')
        info['owner'] = user
        info['type'] = self.MARKET_PROJECT
        project = {}
        project['info'] = info
        fireproject = self.db.firedb.child('projects').child('market').push(project)
        prj_id = fireproject['name']
        self.db.firedb.child('users').child(user).child('projects').child('own').push(
            {'prj_id': prj_id, 'type': self.MARKET_PROJECT})
        self.create_project_link(prj_id, self.MARKET_PROJECT)
        return prj_id

    def create_custom_project(self, info: dict):
        user = info['user']
        info.pop('user')
        info['owner'] = user
        info['type'] = self.CUSTOM_PROJECT
        project = {}
        project['info'] = info
        fireproject = self.db.firedb.child('projects').child('custom').push(project)
        prj_id = fireproject['name']
        self.db.firedb.child('users').child(user).child('projects').child('own').push(
            {'prj_id': prj_id, 'type': self.CUSTOM_PROJECT})
        self.create_project_link(prj_id, self.CUSTOM_PROJECT)
        return prj_id

    def create_project_link(self, prj_id, prj_type):
        self.db.firedb.child('projects').child('links').child(prj_id).set({'type': prj_type})

    OPTIONS = ['info', 'full', 'participants']

    def get_project(self, prj_id, option=OPTIONS[0]):
        prj_type = self.db.firedb.child('projects').child('links').child(prj_id).get().val()['type']
        project = self.db.firedb.child('projects').child(prj_type).child(prj_id).child('info').get().val()
        project['id'] = prj_id
        project = dict(project)
        project['owner'] = self.get_project_owner_info(project)

        if option == 'full':
            project['results'] = self.get_project_results(project)
            project['participants'] = self.get_project_participants(project)

        if option == 'participants':
            project['participants'] = self.get_project_participants(project)

        return project

    def get_project_owner_info(self, project):
        user = self.db.firedb.child('users').child(project['owner']).child('details').get().val()
        return dict(user)

    def get_project_results(self, project):
        res_keys = self.db.firedb.child('projects').child(project['type']).child(project['id']).child(
            'results').shallow().get().val()

        results = []
        if res_keys:
            for key in res_keys:
                res_info = self.db.firedb.child('projects').child(project['type']).child(project['id']).child(
                    'results').child(key).get().val()
                user = self.db.firedb.child('users').child(res_info['user'])
                user = user.child('details').get().val()
                res_info['user'] = dict(user)
                res_info['model'] = self.model_service.get_model(res_info['model'])
                results.append(res_info)

        results = self.sort_results(project, results)
        return results

    def get_project_participants(self, project):
        res_keys = self.db.firedb.child('projects').child(project['type']).child(project['id']).child(
            'participants').shallow().get().val()

        participants = {}
        if res_keys:
            for key in res_keys:
                participant_info = self.db.firedb.child('projects').child(project['type']).child(project['id']).child(
                    'participants').child(key).get().val()

                user_key = participant_info['user']
                user = self.db.firedb.child('users').child(user_key).child('details').get().val()
                participants[user_key] = dict(user)

        return participants


    def get_projects_by_user(self, user, type: str):
        project_keys = self.db.firedb.child('users').child(user).child('projects').child(type).shallow().get().val()

        projects = []
        if project_keys:
            for key in project_keys:
                prj_info = self.db.firedb.child('users').child(user).child('projects').child(type).child(key).get(0).val()
                project = self.get_project(prj_info['prj_id'])
                projects.append(dict(project))
        return projects


    CHECK_SUBJECT = ['market', 'custom']


    def create_check_data(self, info, check_subject=CHECK_SUBJECT[0]):
        if check_subject == 'market':
            self.db.firedb.child('projects').child(info['prj_type']).child(info['project']).child('results').child(
                info['user']).set(info)
            # I just reqrite new information, but we have to deal with uploaded pickle (DELETE MB?)
        if check_subject == 'custom':
            self.db.firedb.child('projects').child(info['prj_type']).child(info['project']).child('results').push(info)


    def add_participant(self, project, user):
        party_users = self.get_party_users(project)
        if not user['id'] in party_users:
            self.db.firedb.child('projects').child(project['type']).child(project['id']).child('participants').push(
                {'user': user['id']})
            self.db.firedb.child('users').child(user['id']).child('projects').child('party').push(
                {'prj_id': project['id'], 'type': project['type']})


    def get_party_users(self, project):
        project = self.get_project(project['id'], 'participants')
        return project['participants']

    def sort_results(self, project, results):
        if (project.get('eval_rules') and 'Mean absolute deviation'.lower() == project.get('eval_rules').lower()):
                results.sort(key = self.sort_results_key)

        return results

    def sort_results_key(self, val):
        return val['result']

    def remove_project(self, project_id):
        project_type = self.db.firedb.child('projects').child('links').child(project_id).get().val().get('type')
        self.db.firedb.child('projects').child('links').child(project_id).remove()
        self.db.firedb.child('projects').child(project_type).child(project_id).remove()
