from Algoritma.services.db_servise import FirebaseService


class ModelService:
    __instance = None

    def __init__(self):
        self.db = FirebaseService.getInstance()

    @classmethod
    def getInstance(self):
        if not self.__instance:
            self.__instance = ModelService()
        return self.__instance

    def create_model(self, info: dict):
        user = info["user"]
        firemodel = self.db.firedb.child('models').push(info)
        self.db.firedb.child('users').child(user).child('models').push({"mid": firemodel["name"], "name": info["name"]})

        return firemodel

    def get_model(self, mid):
        model = self.db.firedb.child('models').child(mid).get().val()
        return model