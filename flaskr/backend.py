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

    def __init__(self, storage_client=storage.Client(), mock_file = open):
        self.pages = []
        self.myStorageClient = storage_client
        self.content_bucket = self.myStorageClient.bucket('wiki-contents')
        self.user_bucket = self.myStorageClient.bucket('users-passwds')
        self.page = None
        self.user = 0
        self.opener = mock_file
    
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
        # @4 This throws a 404 error if there's no
        # page with that name. Not in the rubric,
        # though, so no ding.
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
        # @2 You need to reset self.pages here or
        # you'll accumulate duplicates. -1
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

        # For future reference, I'd recommend abstracting
        # out the blob.upload_from_filename stuff and
        # having this method just accept the string or bytes
        # you want to upload. I'd wager it'd make testing
        # much easier.

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
        # This sort of nested conditional structure is
        # suboptimal. Hides the logic at a higher level
        # of indentation and forces the reader to 
        # mentally track what conditions are true as
        # they're reading the code. Instead, consider
        # ```
        # if self.user_bucket.get_blob(username):
        #       return False
        # blob = ...
        # ```

        if not self.user_bucket.get_blob(username):
            blob = self.user_bucket.blob(username)
            prefix = "saltymelon"
            # `m` is only used in the `if` check; why
            # define it here?
            m = hashlib.sha256()
            m.update(bytes(prefix+password, 'utf-8'))
            # Mixing test logic in with your production
            # logic is bad practice as it makes it
            # harder for others to reason about what's
            # happening. Not dinging as this shouldn't
            # cause any failures in prod (unlike LeBron
            # James), but definitely remind me to cover
            # this sort of thing in our meeting if I forget.
            if not isinstance(blob, str):
                # This should be `with blob.open('wb')`.
                # It's probably leaking, but that's an
                # implementation detail of StorageClient
                # so I can't say for sure
                f1 = blob.open('wb')
                f1.write(bytes(m.hexdigest(), 'utf-8'))
                user = User(blob.name)
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
            n.update(bytes(prefix+password, 'utf-8')) 
            f1 = blob.open('r')
            password1 = str(f1.read())
            # Not great practice to print peoples' plain-text
            # passwords in prod. Logs are usually saved
            # somewhere for at least awhile.
            print(password1)
            hashed_input_pword1 = str(bytes(n.hexdigest(), 'utf-8').decode('utf-8'))
            print(hashed_input_pword1)
            if password1 == hashed_input_pword1:
                user = User(blob.name)
                # @3 I recognize this is probably for
                # testing, but this shouldn't be left
                # in for production code. Now LeBron
                # James can never use your site :( -1
                if blob.name != "LeBron James":
                    login_user(user)
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
