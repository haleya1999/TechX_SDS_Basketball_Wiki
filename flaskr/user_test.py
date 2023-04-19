from flaskr.backend import User, Backend
import pytest
from unittest.mock import MagicMock, patch, Mock, mock_open
from flask_login import LoginManager
from flask import Flask
from collections import defaultdict

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
        
@pytest.fixture
def create_app():
    app = Flask(__name__)
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)

    # with app.app_context():
    #     yield

    return app


class MockFile:

    def __init__(self):
        pass

    def read(self):
        print("password")
        return "cd2ba0b3dfc7ac936f95bababc0c4069f6274eaf1798990d77a293a638a7b07a"


class MockBlob:

    def __init__(self, username):
        self.name = username        

    def open(self, filename):
        return MockFile()

    def __enter__(self):
        return self


class MockBucket:

    def __init__(self):
        self.blobs = defaultdict(MockBlob)

    def blob(self, name):
        return "LBJ"

    def get_blob(self, username):
        blobs = {"LeBron James", "Stephen Curry", "Bill Russel", "Larry Bird"}
        for name in blobs:
            if username == name:
                return MockBlob(username)
        return False


class MockStorageClient:

    def __init__(self, login_info=None):
        self.login_info = login_info
        self.bucket = defaultdict(MockBucket)

    def list_blobs(self, name, prefix=""):
        return ["LeBron James", "Stephen Curry", "Bill Russel", "Larry Bird"]

    def bucket(self, bucket_name=None):
        mock_bucket = MockBucket()
        return MockBucket()


def test_sign_up():
    mock_storage_client = MockStorageClient()
    backend_test = Backend(mock_storage_client)
    assert backend_test.sign_up("Kyrie Irving", "password") == True
    assert backend_test.sign_up("Jamal Crawford", "password") == True


def test_sign_up_with_existing_username():
    mock_storage_client = MockStorageClient()
    backend_test = Backend(mock_storage_client)
    assert backend_test.sign_up("LeBron James", "password") == False
    assert backend_test.sign_up("Bill Russel", "password") == False


def test_login_with_invalid_username():
    mock_storage_client = MockStorageClient()
    backend_test = Backend(mock_storage_client)
    assert backend_test.sign_in("Kyrie Irving", "password") == False
    assert backend_test.sign_in("Jamal Crawford", "password") == False


# with app.app_context():
def test_login_with_valid_username():
    mock_storage_client = MockStorageClient()
    backend_test = Backend(mock_storage_client)
    assert backend_test.sign_in("LeBron James", "password") == True
    assert backend_test.sign_in("LeBron James", "notpassword") == False
