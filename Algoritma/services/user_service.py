from Algoritma.services.db_servise import FirebaseService
from Algoritma.services.file_service import FileService
from Algoritma.services.project_service import ProjectService


class UserService:
    __instance = None

    def __init__(self):
        self.db = FirebaseService.getInstance()
        self.file_service = FileService.getInstance()
        self.project_service = ProjectService.getInstance()

    @classmethod
    def getInstance(self):
        if not self.__instance:
            self.__instance = UserService()
        return self.__instance

    def signin(self, email, password):
        user = self.fireauth.sign_in_with_email_and_password(email, password)
        return user

    def create_account(self, info):
        # check account
        user = self.db.fireauth.create_user_with_email_and_password(info["email"], info["password"])
        uid = user["localId"]
        data = {"name": info["name"], "role": info["role"], "email": info["email"]}
        if info["image"]:
            image_bucket, image_path = self.file_service.upload_file(info["image"], 13)
            data["image"] = image_path
        self.save_user_info(uid, data)
        return user

    def save_user_info(self, uid, info: dict):
        data = {"name": info["name"], "role": info["role"], "image": info["image"], "email": info["email"]}
        self.db.firedb.child("users").child(uid).child("details").set(data)

    def get_user_info(self, idtoken):
        account = self.db.fireauth.get_account_info(idtoken)
        account = account['users'][0]['localId']

        user = self.db.firedb.child("users").child(account).child("details").get().val()
        user["id"] = account
        user = dict(user)

        return user

    def get_user_models(self, user):
        model_keys = self.db.firedb.child('users').child(user).child("models").shallow().get().val()

        models = []
        if model_keys:
            for key in model_keys:
                model = self.db.firedb.child('users').child(user).child("models").child(key).get().val()
                models.append(dict(model))

        return models

    OWN_PROJECTS = "own"
    PARTY_PROJECTS = "party"

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
                temp_user = self.db.firedb.child('users').child(key).child("details").get().val()
                if (temp_user.get("email") == email):
                    user = temp_user
                    user["id"] = key
                    break

        return user