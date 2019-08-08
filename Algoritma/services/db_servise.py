import pyrebase
import Algoritma.utils as utils
import firebase_admin
from firebase_admin import credentials, firestore, storage

ID_SIZE = 9

config = {
    "apiKey": "AIzaSyCEEBWHipEhE8wjQNXVtmd0CDUUEUq9kGQ",
    "authDomain": "innosoft-django.firebaseapp.com",
    "databaseURL": "https://innosoft-django.firebaseio.com",
    "projectId": "innosoft-django",
    "storageBucket": "innosoft-django.appspot.com",
    "messagingSenderId": "728530690260",
    "appId": "1:728530690260:web:790af9c28f5476e8"
}

certificate_file = 'innosoft-django-firebase-adminsdk-kml31-03d2439b89.json'
bucket_path = 'innosoft-django.appspot.com'


class FirebaseService:
    __instance = None
    def __init__(self):
        self.config = config
        self.firebase = pyrebase.initialize_app(config)
        self.fireauth = self.firebase.auth()
        self.firedb = self.firebase.database()

        self.cred = credentials.Certificate(certificate_file)
        firebase_admin.initialize_app(self.cred, {
            'storageBucket': bucket_path
        })
        self.db = firestore.client()
        self.bucket = storage.bucket()

    @classmethod
    def getInstance(self):
        if not self.__instance:
            self.__instance = FirebaseService()
        return self.__instance