# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
import hashlib
from flask import request, render_template



class Backend:

    def __init__(self):
        self.pages = []
        self.storage_client = storage.Client()
        self.content_bucket = self.storage_client.bucket('wiki-contents')
        self.user_bucket = self.storage_client.bucket('users-passwds')

    def get_wiki_page(self, name):
        pass

    def get_all_page_names(self):
        bucket_name = "wiki-contents"
        all_pages = self.storage_client.list_blobs(bucket_name)
        for page in all_pages:
            self.pages.append(page)
        return self.pages

    def upload(self):
        pass

    def sign_up(self, username, password):
        if not self.user_bucket.get_blob(username):
            blob = self.user_bucket.blob(username)
            prefix = "saltymelon"
            m = hashlib.sha256()
            m.update(bytes(prefix+password, 'utf-8'))
            with blob.open('wb') as f:
                f.write(bytes(m.hexdigest(), 'utf-8'))
            return True
        else:
            return False
        

    def sign_in(self, username, password):
        blob = self.user_bucket.get_blob(username)
        with blob.open('r') as f:
            if f.read() == password:
                return True
            else:
                return False

    def get_image(self, img_name):
        # for a given image name in GCS Bucket, make image public and return public url
        blob = self.content_bucket.blob(img_name)
        blob.make_public()
        return blob.public_url
