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
        if type(self.myStorageClient) == type(storage.Client()):
            self.content_bucket = self.myStorageClient.bucket('wiki-contents')
            self.user_bucket = self.myStorageClient.bucket('users-passwds')
        else:
            self.content_bucket = self.myStorageClient.bucket['wiki-contents']
            self.user_bucket = self.myStorageClient.bucket['users-passwds']

        self.page = None
        self.user = User("not-logged-in")
        self.username = ''
        self.opener = mock_file
        self.metadata_page = None
        self.pages_by_name = defaultdict(list)

        self.pages_by_category = {
            'teams': {
                "Atlanta Hawks": [],
                "Boston Celtics": [],
                "Brooklyn Nets": [],
                "Charlotte Hornets": [],
                "Chicago Bulls": [],
                "Cleveland Cavaliers": [],
                "Dallas Mavericks": [],
                "Denver Nuggets": [],
                "Detroit Pistons": [],
                "Golden State Warriors": [],
                "Houston Rockets": [],
                "Indiana Pacers": [],
                "Los Angeles Clippers": [],
                "Los Angeles Lakers": [],
                "Memphis Grizzlies": [],
                "Miami Heat": [],
                "Milwaukee Bucks": [],
                "Minnesota Timberwolves": [],
                "New Orleans Pelicans": [],
                "New York Knicks": [],
                "Oklahoma City Thunder": [],
                "Orlando Magic": [],
                "Philadelphia 76ers": [],
                "Phoenix Suns": [],
                "Portland Trail Blazers": [],
                "Sacramento Kings": [],
                "San Antonio Spurs": [],
                "Toronto Raptors": [],
                "Utah Jazz": [],
                "Washington Wizards": [],               
            },
            'years': {
                1940: [],
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
        self.fill_sort_by_name()
        print(self.pages_by_category)
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
        players_file = "all-players/all_players.pkl"
        blob = self.content_bucket.blob(players_file)
        try:
            with blob.open("rb") as dictionary:
                self.all_players = pickle.load(dictionary)    
        except TypeError as e:
            raise e              
        except:
            self.all_players = {}     
                    
        all_players_dict = self.all_players
        
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
        if type(self.myStorageClient) == type(storage.Client()):        
            metadata_file = f"{name[5:-4]}-metadata.txt"
            self.update_metadata(metadata_file)
        return self.page
    
    def get_searched_pages(self, text):
        self.searched_pages = []
        bucket_name = "wiki-contents"
        all_pages = self.myStorageClient.list_blobs(bucket_name, prefix="docs/")

        processed_text = text.lower()
        processed_text.replace("-", " ")
        text_list = processed_text.split()
        num_words = len(text_list)
        search_results_counter = {}
        search_results = [] 
        print("pages by name")
        print(self.pages_by_name)

        # ensures duplicate pages are not returned
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
        in_position = set()
        in_draft_year = set()
        in_team = set()  
        for player in valid_pages:
            name = player.name
            name = name[5:]            
            if selected_position != "all_positions" and name in self.pages_by_category['positions'][selected_position]:
                in_position.add(player)            
            if selected_draft_year != "all_decades" and name in self.pages_by_category['years'][int(selected_draft_year)]:
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
        elif selected_position != "all_positions":
            return list(in_position)
        elif selected_draft_year != "all_decades":
            return list(in_draft_year)
        elif selected_teams[0] != "all_teams":
            return list(in_team)
        else:
            print("12345")
            pages_without_iterator = []
            for player in valid_pages:
                pages_without_iterator.append(player)
            return pages_without_iterator

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
        self.pages = []
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
        blob.upload_from_filename(
            final_file_name, if_generation_match=generation_match_precondition)


    def update_metadata(self, source_name):
        '''
        Updates metadata for specific page.

        Args:
            self: instance of the class.
            source_name: name of text file that User clicked on.

        Returns:
            N/A

        Raises:
            N/A
        '''
        print(source_name)
        print("gets to metadata")
        self.metadata_page = self.content_bucket.blob(f"metadata/{source_name}")
        modified_data = None
        print(self.metadata_page)
        with self.metadata_page.open("r") as metadata_page:
            data = metadata_page.readlines()
            print(1)
            print(data)
            visits = data[2]
            amt_visits = int(visits[-2])
            amt_visits += 1
            print(amt_visits)
            data[2] = f"Number of Vists: {amt_visits}\n"
            modified_data = data
            print(modified_data)
        with self.metadata_page.open("w") as metadata_page:
            metadata_page.writelines(modified_data)
        blob = self.metadata_page
        blob.upload_from_filename(source_name)

        
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
            if not isinstance(blob, str):
                f1 = blob.open('r')
            password1 = str(f1.read())
            hashed_input_pword1 = str(
                bytes(n.hexdigest(), 'utf-8').decode('utf-8'))
            if password1 == hashed_input_pword1:
                user = User(blob.name)
                if blob.name != "LeBron James":
                    login_user(user)
                    self.username = username
                    print("User logged in")
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

    def save_edits(self, filename, text):
        '''
        This method uploads newly edited wiki page back to GCS buckets.

        Args:
            self: An instance of the class.
            filename: The file that is being edited.
            text: The updated text that goes on the wiki page.

        Returns:
            N/A
        
        Raises:
            N/A
        '''
        blob = self.content_bucket.blob(filename)
        with blob.open("w") as blob:
            blob.writelines(text)
        blob.upload_from_filename(filename)
    

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
            if not isinstance(page, str):
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

    def format_page_name(self, filename = None):
        """Formats filename to readable string containing the file's player name

        Args:
            self: Instance of the class.
            filename: .txt file of player

        Returns:
            String of player's name
        Raises:
            N/A
        """
        if filename.name:
            name = filename.name[5:-4]
            name.replace("-", " ")
            text_list = name.split()
            for item in text_list:
                item[0] = item[0].upper()
            return text_list.join(" ")                
        else:
            return ""

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

