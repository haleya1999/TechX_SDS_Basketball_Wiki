# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
import os

storage_client = storage.Client()
content_bucket = storage_client.bucket('wiki-contents')
user_bucket = storage_client.bucket('users-passwds')

class Backend:

    def __init__(self, storage_client=storage_client):
        self.pages = []
        self.myStorageClient = storage_client
    def get_wiki_page(self, name):
        pass

    def get_all_page_names(self):
        bucket_name = "wiki-contents"
        all_pages = self.myStorageClient.list_blobs(bucket_name)
        for page in all_pages:
            self.pages.append(page)
        return self.pages

    def upload(self, source_name):
        photo_extensions = {"jpg", "jpeg", "png", "gif"}

        if source_name.rsplit('.', 1)[1].lower() in photo_extensions:
            blob = content_bucket.blob("pictures/" + source_name)
            generation_match_precondition = 0
            blob.upload_from_filename(source_name, if_generation_match=generation_match_precondition)
        else:
            blob = content_bucket.blob("docs/" + source_name)
            generation_match_precondition = 0
            blob.upload_from_filename(source_name, if_generation_match=generation_match_precondition)     
        os.remove(source_name)

    def sign_up(self):
        pass

    def sign_in(self):
        pass

    def get_image(self, img_name):
        # for a given image name in GCS Bucket, make image public and return public url
        blob = content_bucket.blob("pictures/" + img_name)
        blob.make_public()
        return blob.public_url
