from django.conf import settings
from django.core.files.storage import Storage


class FastDFSStorage(Storage):
    def __init__(self):
        
        self.base_url = settings.FDFS_BASE_URL

    def _open(self, name, mode='rb'):
        pass
    def _save(self, name, content, max_length=None):
        pass

    def url(self, name):

        return self.base_url + name