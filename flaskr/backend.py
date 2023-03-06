# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage

storage_client = storage.Client()
content_bucket = storage_client.bucket('wiki-contents')
user_bucket = storage_client.bucket('users-passwds')

class Backend:

    def __init__(self):
        self.page_names = []
        
    def get_wiki_page(self, name):
        pass

    def get_all_page_names(self):
        bucket_name = "wiki-contents"
        all_names = storage_client.list_blobs(bucket_name)
        for page_name in all_names:
            self.page_names.append(page_name)
        return self.page_names

    def upload(self):
        pass

    def sign_up(self):
        pass

    def sign_in(self):
        pass

    def get_image(self, img_name):
        # for a given image name in GCS Bucket, make image public and return public url
        blob = content_bucket.blob(img_name)
        blob.make_public()
        return blob.public_url
