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
from collections import defaultdict
from flask_login import login_user, logout_user
from datetime import datetime
import ast
from collections import defaultdict
import json
import pickle

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

        print(type(self.myStorageClient))
        if type(self.myStorageClient) == type(storage.Client()):
            self.content_bucket = self.myStorageClient.bucket('wiki-contents')
            self.user_bucket = self.myStorageClient.bucket('users-passwds')
        else:
            self.content_bucket = self.myStorageClient.bucket['wiki-contents']
            self.user_bucket = self.myStorageClient.bucket['users-passwds']

        self.page = None
        self.user = User("not-logged-in")
        self.opener = mock_file
        self.pages_by_name = defaultdict(list)

        self.pages_by_category = {
            'teams': {},
            'years': {
                1950: [],
                1960: [],
                1970: [],
                1980: [],
                1990: [],
                2000: [],
                2010: [],
                2020: []
            },
            'positions': {
                'center': [],
                'power-forward': [],
                'small-forward': [],
                'point-guard': [],
                'shooting-guard': []
            }
        }
        
        self.categorize_players()
        print(self.pages_by_category)
        self.fill_sort_by_name()

        self.search_results = []
        # self.fill_sort_by_category()

    def categorize_players(self):
        """update category dictionary with saved data in GCS

        Args:
            self: Instance of the class.
            

        Returns:
            N/A
        Raises:
            N/A
        """
        all_players_file = self.content_bucket.blob("all-players/all_players.txt")
        with all_players_file.open("r") as all_players_file:
                json_dict = all_players_file.read()

        all_players_dict = eval(json_dict.replace("'", "\""))
        print(all_players_dict)
        print(type(all_players_dict))
        for player in all_players_dict:
            if player != "all_players.txt":
                draft_year = all_players_dict[player]['draft_year']
                draft_year = int(draft_year)
                draft_decade = round((draft_year - 5)/10)*10
                self.pages_by_category['years'][draft_decade].append(player)
                
                position = all_players_dict[player]['position']
                self.pages_by_category['positions'][position].append(player)

                for team in all_players_dict[player]['teams']:
                    if team not in self.pages_by_category['teams']:
                        self.pages_by_category['teams'][team] = [player]
                    else:
                        self.pages_by_category['teams'][team].append(player)                             
                             
        
        self.search_results = []

        
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
        self.page = self.content_bucket.blob(name)
        return self.page
    
    def get_searched_pages(self, text):
        self.searched_pages = []
        bucket_name = "wiki-contents"
        all_pages = self.myStorageClient.list_blobs(bucket_name, prefix="docs/")
        print("text:")
        print(text)
        processed_text = text.lower()
        processed_text.replace("-", " ")
        text_list = processed_text.split()
        num_words = len(text_list)
        search_results_counter = {}
        search_results = [] 
        print("pages by name")
        print(self.pages_by_name)
        for name in text_list:
            if name in self.pages_by_name:
                if self.pages_by_name[name][0] in search_results_counter:
                    search_results_counter[self.pages_by_name[name][0]] += 1
                else:
                    search_results_counter[self.pages_by_name[name][0]] = 1

        for page in search_results_counter:
            if search_results_counter[page] >= num_words:
                search_results.append(page)
        
        for page in all_pages:
            if page.name in search_results:
                self.searched_pages.append(page)
        print(self.searched_pages)
        return self.searched_pages    

    def search_by_category(self, valid_pages, selected_position, selected_draft_year, selected_teams):
        print(valid_pages)
        in_position = set()
        in_draft_year = set()
        in_team = set()  
        for player in valid_pages:
            name = player.name
            name = name[5:]            
            if selected_position != "all_positions" and name in self.pages_by_category[selected_position]:
                in_position.add(player)            
            if selected_draft_year != "all_decades" and name in self.pages_by_category[selected_draft_year]:
                in_draft_year.add(player) 
            for team in selected_teams:
                if selected_teams[0] != "all_teams" and name in self.pages_by_category['teams'][team]:
                    in_team.add(player)
                    break
        if selected_position != "all_positions" and selected_draft_year != "all_decades" and selected_teams[0] != "all_teams":
            return list(in_position.intersection(in_draft_year, in_team))
        elif selected_position != "all_positions" and selected_draft_year != "all_decades":
            return list(in_position.intersection(in_draft_year))
        elif selected_position != "all_positions" and selected_teams[0] != "all_teams":
            return list(in_position.intersection(in_team))
        elif selected_draft_year != "all_decades" and selected_teams[0] != "all_teams":
            return list(in_draft_year.intersection(in_team))
        

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
        self.pages = []
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
        source = source_name.rsplit('.', 1)
        metadata_file = source[0] + "-metadata"
        final_file_name = metadata_file + ".txt"
        print(final_file_name)
        with open(final_file_name, "w") as f:
            # author, time, visits,
            # number of visits
            # time it was posted
            visits = 0
            posted_at = datetime.now()
            author = self.user.username
            f.write(f"Author: {author}\n")
            f.write(f"Posted at: {posted_at}\n")
            f.write(f"Number of Vists: {visits}\n")
        blob = self.content_bucket.blob("metadata/" + final_file_name)
        generation_match_precondition = 0
        blob.upload_from_filename(
            final_file_name, if_generation_match=generation_match_precondition)

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
                self.user = User(blob.name)
                login_user(self.user)
                return True
            else:
                return True
        else:
            return False

    def sign_in(self, username, password, mock_open=open):
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
            hashed_input_pword1 = str(
                bytes(n.hexdigest(), 'utf-8').decode('utf-8'))
            if password1 == hashed_input_pword1:
                self.user = User(blob.name)
                if blob.name != "LeBron James":
                    login_user(self.user)
                return True
            else:
                return False
        else:
            return False

    def logout(self):
        logout_user()

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


    def update_player_metadata(self, filename, position, draft_year, teams):
        '''
        Adds player information to universal dictionary of all players uploaded 
        to the wiki.

        This will be used to conduct categorical searches on the pages uploaded to
        the wiki.

        Args:
            self: An instance of the class.
            filename: Name of the file user uploaded to the wiki.
            position: Position the player plays that was inputted into HTML form.
            draft_year: Year player was drafted
            teams: List of teams player has played on.

        Returns: 
            N/A
        '''
        players_file = "all-players/all_players.pkl"
        blob = self.content_bucket.blob(players_file)
        try:
            with blob.open("rb") as dictionary:
                self.all_players = pickle.load(dictionary)    
        except TypeError as e:
            raise e              
        except:
            self.all_players = {}     
        with blob.open("wb") as dictionary:
            self.all_players[filename] = {
                'position': position,
                'draft_year': draft_year,
                'teams': teams
            }
            pickle.dump(self.all_players, dictionary)

    def fill_sort_by_name(self):
        """fill a dictionary with names and a list of pages from GCS corresponding to each name

        Args:
            self: Instance of the class.
            

        Returns:
            N/A
        Raises:
            N/A
        """
        bucket_name = "wiki-contents"
        all_pages = self.myStorageClient.list_blobs(bucket_name, prefix="docs/")
        for page in all_pages:
            title = page.name[5:-4]
            names = title.split('-')
            for name in names:
                if name != '':
                    self.pages_by_name[name].append(page.name)

    def update_sort_by_name(self, filename):
        """update name dictionary with info from uploaded files

        Args:
            self: Instance of the class.
            

        Returns:
            N/A
        Raises:
            N/A
        """
        #remove file extension from filename
        title = filename[:-4]
        names = title.split('-')
        for name in names:
            self.pages_by_name[name].append("docs/" + filename)

