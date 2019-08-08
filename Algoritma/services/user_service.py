import re

from Algoritma.services.db_servise import FirebaseService
from Algoritma.services.file_service import FileService
from Algoritma.services.model_service import ModelService
from Algoritma.services.project_service import ProjectService


class UserService:
    __instance = None

    def __init__(self):
        self.db = FirebaseService.getInstance()
        self.file_service = FileService.getInstance()
        self.project_service = ProjectService.getInstance()
        self.model_service = ModelService.getInstance()

    @classmethod
    def getInstance(self):
        if not self.__instance:
            self.__instance = UserService()
        return self.__instance

    def signin(self, email, password):
        user = self.db.fireauth.sign_in_with_email_and_password(email, password)
        return user

    def create_account(self, info):
        # check account
        user = self.db.fireauth.create_user_with_email_and_password(info.get('email'), info.get('password'))
        uid = user.get('localId')
        data = {'name': info.get('name'), 'role': info.get('role'), 'email': info.get('email')}
        if info.get('image'):
            image_bucket, image_path = self.file_service.upload_file(info.get('image'), 13)
            data['image'] = image_path
        self.save_user_info(uid, data)
        return user


    def save_user_info(self, uid, info: dict):
        data = {'name': info.get('name'), 'role': info.get('role'), 'image': info.get('image'), 'email': info.get('email')}
        self.db.firedb.child('users').child(uid).child('details').set(data)

    def get_user_info(self, idtoken):
        account = self.db.fireauth.get_account_info(idtoken)
        account = account['users'][0]['localId']

        user = self.db.firedb.child('users').child(account).child('details').get().val()
        user['id'] = account
        user = dict(user)

        return user

    def get_user_models(self, user):
        model_keys = self.db.firedb.child('users').child(user).child('models').shallow().get().val()

        models = []
        if model_keys:
            for key in model_keys:
                model = self.db.firedb.child('users').child(user).child('models').child(key).get().val()
                model['id'] = key
                models.append(dict(model))

        return models

    OWN_PROJECTS = 'own'
    PARTY_PROJECTS = 'party'

    def get_user_projects(self, user):
        projects = []
        projects.extend(self.project_service.get_projects_by_user(user, self.OWN_PROJECTS))
        projects.extend(self.project_service.get_projects_by_user(user, self.PARTY_PROJECTS))
        return projects

    def get_user_by_email(self, email):
        user_keys = self.db.firedb.child('users').shallow().get().val()

        user = None
        if user_keys:
            for key in user_keys:
                temp_user = self.db.firedb.child('users').child(key).child('details').get().val()
                if (temp_user.get('email') == email):
                    user = temp_user
                    user['id'] = key
                    break
        return user

    def remove_account(self, email, password):
        # try:
        try:
            user = self.signin(email, password)
            try:
                self.remove_user_projects(user.get('localId'))
            except:
                print("project error")

            try:
                self.remove_user_models(user.get('localId'))
            except:
                print("model error")

            try:
                self.db.fireauth.delete_user_account(user.get('idToken'))
            except:
                print("fireauth error")

            try:
                self.db.firedb.child('users').child(user.get('localId')).remove()
            except:
                print("user delete error")
        except:
            print("signin error")
            pass


        # except:
        #     print('error')


    def remove_user_projects(self, user):
        projects = self.get_user_projects(user)
        for project in projects:
            print(project.get('id'))
            self.project_service.remove_project(project.get('id'))

    def remove_user_models(self, user):
        models = self.get_user_models(user)
        for model in models:
            print(model.get('id'))
            self.model_service.remove_user_model(model.get('mid'))

    def get_users_list(self, substring):
        user_keys = self.db.firedb.child('users').shallow().get().val()
        users = []
        if user_keys:
            for key in user_keys:
                temp_user = self.db.firedb.child('users').child(key).child('details').get().val()
                name = temp_user.get('name')
                if (re.match('%s*' % substring, temp_user.get('name'))):
                    user = temp_user
                    user['id'] = key
                    users.append(user)
        return users
