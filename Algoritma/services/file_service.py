from Algoritma.services.db_servise import FirebaseService
import Algoritma.utils as utils

class FileService:
    FILENAME_SIZE = 13

    __instance = None

    def __init__(self):
        self.db = FirebaseService.get_instance()

    @classmethod
    def get_instance(self):
        if not self.__instance:
            self.__instance = FileService()
        return self.__instance

    def upload_file(self, file, nlength=FILENAME_SIZE, extension=None, content_type=None):
        if not extension:
            extension = file.name.split(".")[-1]
        if not content_type:
            content_type = file.content_type
        blobname = "%s.%s" % (utils.generate_rand_name(nlength), extension)
        blob = self.db.bucket.blob(blobname)
        blob.upload_from_file(file, content_type=content_type)
        path = blob.public_url
        return blobname, path

    def upload_file_string(self, file, nlength=FILENAME_SIZE, extension=None, content_type="text/plain"):
        if not extension:
            extension = file.name.split(".")[-1]
        if not content_type:
            content_type = file.content_type
        blobname = "%s.%s" % (utils.generate_rand_name(nlength), extension)
        blob = self.db.bucket.blob(blobname)
        blob.upload_from_string(file, content_type=content_type)
        path = blob.public_url
        return blobname, path

    def save_image(self, image):
        firename = "%s.%s" % (utils.generate_rand_name(13), image.name.split(".")[-1])
        image_path = self.upload_file(image, firename)
        return image_path

    def get_file_string(self, name):
        model_blob = self.db.bucket.get_blob(name)
        model_pickle = model_blob.download_as_string()
        return model_pickle