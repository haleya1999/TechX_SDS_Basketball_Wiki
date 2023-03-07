# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
import os

storage_client = storage.Client()
content_bucket = storage_client.bucket('wiki-contents')
user_bucket = storage_client.bucket('users-passwds')

class Backend:

    def __init__(self):
        self.pages = []
        
    def get_wiki_page(self, name):
        pass

    def get_all_page_names(self):
        bucket_name = "wiki-contents"
        all_pages = storage_client.list_blobs(bucket_name)
        for page in all_pages:
            self.pages.append(page)
        return self.pages

    def upload(self, source_name):
        blob = content_bucket.blob(source_name)
        generation_match_precondition = 0
        blob.upload_from_filename(source_name, if_generation_match=generation_match_precondition)
        os.remove(source_name)
        

    def sign_up(self):
        pass

    def sign_in(self):
        pass

    def get_image(self, img_name):
        # for a given image name in GCS Bucket, make image public and return public url
        blob = content_bucket.blob(img_name)
        blob.make_public()
        return blob.public_url
