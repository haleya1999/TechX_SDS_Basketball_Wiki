"""Includes the Backend class.

The Backend class handles and returns data from Google Cloud Storage. 
This class is used to fetch html pages, get data from GCS buckets, upload 
data to GCS buckets, and keep track of users' personal data within GCS buckets/

Typical usage example:

  backend = Backend()
  all_pages = backend.get_all_page_names()
"""
# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
import hashlib
from flask import request, render_template

import os


class Backend:
    """Class that takes care of data through Google Cloud Storage

    Within this class, we store, fetch, upload, and encrypt user data. 
    The backend communicates with our storage client: Google Cloud
    Storage. 

    Attributes:
        pages: a list of all the pages that have been uploaded to the wiki. 
        myStorageClient: storage client that we read and write data to.
        content_bucket: storage bucket with all wiki contents (imgs, pages, etc.)
        user_bucket: storage bucket that stores usernames and passwords
        page: specific page that is being returned to webpage.
    """

    def __init__(self, storage_client=storage.Client()):
        self.pages = []
        self.myStorageClient = storage_client
        self.content_bucket = self.myStorageClient.bucket('wiki-contents')
        self.user_bucket = self.myStorageClient.bucket('users-passwds')
        self.page = None

    
    def get_wiki_page(self, name):
        """Fetches specific wiki page from content bucket.

        Retrieves wiki page from Google Cloud Storage based on the name provided.

        Args:
            self: Instance of the class.
            name: Name of specific wiki page that will be displayed.

        Returns:
            The wiki file that was uploaded with given name.

        Raises:
            N/A
        """
        bucket_name = "wiki-contents"
        self.page = self.content_bucket.blob(name)
        return self.page

    def get_all_page_names(self):
        """Returns all wiki pages.

        Retrieves all wiki pages that have been uploaded to the wiki website.

        Args:
            self: Instance of the class.

        Returns:
            A list of all of the page files stored in content bucket.

        Raises:
            N/A
        """
        bucket_name = "wiki-contents"
        all_pages = self.myStorageClient.list_blobs(bucket_name, prefix="docs/")
        for page in all_pages:
            self.pages.append(page)
        return self.pages

    def upload(self, source_name):
        photo_extensions = {"jpg", "jpeg", "png", "gif"}

        if source_name.rsplit('.', 1)[1].lower() in photo_extensions:
            blob = self.content_bucket.blob("pictures/" + source_name)
            generation_match_precondition = 0
            blob.upload_from_filename(source_name, if_generation_match=generation_match_precondition)
        else:
            blob = self.content_bucket.blob("docs/" + source_name)
            generation_match_precondition = 0
            blob.upload_from_filename(source_name, if_generation_match=generation_match_precondition)     
        os.remove(source_name)

    def sign_up(self, username, password):
        if not self.user_bucket.get_blob(username):
            blob = self.user_bucket.blob(username)
            prefix = "saltymelon"
            m = hashlib.sha256()
            m.update(bytes(prefix+password, 'utf-8'))
            with blob.open('wb') as f:
                f.write(bytes(m.hexdigest(), 'utf-8'))
            self.user = username
            return True
        else:
            return False
        
    def sign_in(self, username, password):
        blob = self.user_bucket.get_blob(username)
        if blob:
            prefix = "saltymelon"
            n = hashlib.sha256()
            n.update(bytes(prefix+password, 'utf-8'))
            with blob.open('r') as f:
                password = str(f.read())
                hashed_input_pword = str(bytes(n.hexdigest(), 'utf-8').decode('utf-8'))
                if password == hashed_input_pword:
                    self.user = username
                    return True
                else:
                    return False
        else:
            return False

    def get_image(self, img_name):
        # for a given image name in GCS Bucket, make image public and return public url
        blob = self.content_bucket.blob("pictures/" + img_name)
        blob.make_public()
        return blob.public_url
