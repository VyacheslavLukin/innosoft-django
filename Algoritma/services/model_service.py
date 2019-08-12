from Algoritma.services.db_servise import FirebaseService


class ModelService:
    __instance = None

    def __init__(self):
        self.db = FirebaseService.get_instance()

    @classmethod
    def get_instance(self):
        if not self.__instance:
            self.__instance = ModelService()
        return self.__instance

    def create_model(self, info: dict):
        user = info.get('user')
        firemodel = self.db.firedb.child('models').push(info)
        self.db.firedb.child('users').child(user).child('models').push({'mid': firemodel.get('name'), 'name': info.get('name')})

        return firemodel

    def get_model(self, mid):
        model = self.db.firedb.child('models').child(mid).get().val()
        return model

    def remove_user_model(self, mid):
        self.db.firedb.child('models').child(mid).remove()
