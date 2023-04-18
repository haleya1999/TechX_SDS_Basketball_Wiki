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
from flask import request, render_template, session, Flask
import os
from flask_login import login_user, logout_user
from datetime import datetime


class User:

    def __init__(self, username):
        self.username = username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username


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

    def __init__(self, storage_client=storage.Client(), mock_file=open):
        self.pages = []
        self.myStorageClient = storage_client
        if storage_client == storage.Client():
            self.content_bucket = self.myStorageClient.bucket('wiki-contents')
            self.user_bucket = self.myStorageClient.bucket('users-passwds')
        else:
            self.content_bucket = self.myStorageClient.bucket['wiki-contents']
            self.user_bucket = self.myStorageClient.bucket['users-passwds']
        self.page = None
        self.user = 0
        self.opener = mock_file
        self.metadata_file = ""
        self.username = ""

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
        """Returns all wiki pages.

        Retrieves all wiki pages that have been uploaded to the wiki website.

        Args:
            self: Instance of the class.

        Returns:
            A list of all of the page files stored in content bucket.

        Raises:
            N/A
        """

        photo_extensions = {"jpg", "jpeg", "png", "gif"}

        if source_name.rsplit('.', 1)[1].lower() in photo_extensions:
            blob = self.content_bucket.blob("pictures/" + source_name)
            generation_match_precondition = 0
            blob.upload_from_filename(
                source_name, if_generation_match=generation_match_precondition)
        else:
            blob = self.content_bucket.blob("docs/" + source_name)
            generation_match_precondition = 0
            blob.upload_from_filename(
                source_name, if_generation_match=generation_match_precondition)
            self.create_metadata(source_name)
        os.remove(source_name)
                       

    def create_metadata(self, source_name):
        '''
        Creates a metadata file to add to GCS buckets to keep
        track and update text files metadata.

        Args:
            self: instance of the class
            source_name: the name of the text file that was
            uploaded to the wiki.

        Returns:
            N/A

        Raises: 
            N/A
        '''
        source = source_name.rsplit('.', 1)
        final_file_name = f"{source[0]}-metadata.txt"
        self.metadata_file = final_file_name
        if self.opener == open:
            f = self.opener(final_file_name, "w")
        else:
            f = self.opener
        visits = 0
        posted_at = datetime.now()
        author = self.username
        f.write(f"Author: {author}\n")
        f.write(f"Posted at: {posted_at}\n")
        f.write(f"Number of Vists: {visits}\n")
        f.close()
        blob = self.content_bucket.blob("metadata/" + final_file_name)
        generation_match_precondition = 0
        blob.upload_from_filename(final_file_name, if_generation_match=generation_match_precondition)

    def sign_up(self, username, password):
        """Uploads file with hashed password into the user_bucket and uses the username as the key.

        Args:
            self: Instance of the class.
            username: string inputted into username field in form on signup.html
            password: string inputted into password field in form on signup.html
        Returns:
            True if username does not already exist in the users-passwds bucket
            else False

        Raises:
            N/A
        """
        if not self.user_bucket.get_blob(username):
            blob = self.user_bucket.blob(username)
            prefix = "saltymelon"
            m = hashlib.sha256()
            m.update(bytes(prefix + password, 'utf-8'))
            if not isinstance(blob, str):
                f1 = blob.open('wb')
                f1.write(bytes(m.hexdigest(), 'utf-8'))
                user = User(blob.name)
                self.username = username
                login_user(user)
                return True
            else:
                return True
        else:
            return False

    def sign_in(self, username, password):
        """Finds filename that matches with inputted username and evaluates if the inputted password is correct.

        Args:
            self: Instance of the class.
            username: string inputted into username field in form on login.html
            password: string inputted into password field in form on login.html
        Returns:
            True if username/password combo is correct
            else False

        Raises:
            N/A
        """
        blob = self.user_bucket.get_blob(username)
        if blob:
            prefix = "saltymelon"
            n = hashlib.sha256()
            n.update(bytes(prefix + password, 'utf-8'))
            f1 = blob.open('r')
            password1 = str(f1.read())
            print(password1)
            hashed_input_pword1 = str(
                bytes(n.hexdigest(), 'utf-8').decode('utf-8'))
            print(hashed_input_pword1)
            if password1 == hashed_input_pword1:
                user = User(blob.name)
                if blob.name != "LeBron James":
                    login_user(user)
                    self.username = username
                    print("User logged in")
                # last stopped here - Maize
                return True
            else:
                return False
        else:
            return False

    def logout(self):
        logout_user()
        # return redirect()

    def get_image(self, img_name):
        """Get specified image public url

        Retrieves public url of image in GCS bucket

        Args:
            self: Instance of the class.
            

        Returns:
            A list of all of the page files stored in content bucket.

        Raises:
            N/A
        """
        # for a given image name in GCS Bucket, make image public and return public url
        print(img_name)
        blob = self.content_bucket.blob("pictures/" + img_name)
        print(blob)
        blob.make_public()
        return blob.public_url
