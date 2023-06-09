import pytest
from flaskr.backend import Backend
from collections import defaultdict
from unittest.mock import MagicMock, patch, Mock, mock_open

# TODO(Project 1): Write tests for Backend methods.


class MockBlob:

    def __init__(self, filename = "LBJ"):
        self.name = filename

    def __enter__(self):
        return self
    
    def __exit__(self, _1, _2, _3):
        pass

    def open(self, param):
        return self          

    def read(self, _):
        return bytes()

    def readline(self):
        return bytes()
    
    def readlines(self):
        return "Test String"

    def write(self, contents):
        pass

    def upload_from_filename(self, filename, if_generation_match):
        pass


class MockBucket:

    def __init__(self):
        self.blobs = defaultdict(MockBlob)

    def blob(self, name):
        return self.blobs[name]
    
    def get_blob(self, name):
        return self.blobs[name]

    def image(self, name="test_img"):
        self.name = name
        return "test_img.jpg"


class MockStorageClient:

    def __init__(self):
        self.bucket = defaultdict(MockBucket)

    def list_blobs(self, name, prefix=""):
        return [MockBlob("docs/lebron-james.txt"), MockBlob("docs/stephen-curry.txt"), MockBlob("docs/Bill-Russel.txt"), MockBlob("docs/larry-bird.txt"), MockBlob("docs/james-harden.txt")]

    def bucket(self, bucket_name):
        return self.bucket[bucket_name]

@pytest.fixture
def open_mock(content):
    test_file = ""
    return mock_open(content, test_file)

class mockstorage:

    def __init__(self):
        pass

    def list_blobs(self, source, prefix=""):
        return [MockBlob("docs/test-file.txt"), MockBlob("docs/file-name.txt")]

    def bucket(self, name):
        pass

class MockFile:

    def __init__(self, filename, param):
        self.content = ""
        self.filename = ""

    def open(self):
        pass

    def set_filename(self, name):
        self.filename = name

    def write(self, content):
        self.content = content

    def close(self):
        return self

def test_get_all_pages():
    mock_storage_client = MockStorageClient()    
    backend_test = Backend(mock_storage_client)
    all_pages = backend_test.get_all_page_names()
    assert all_pages[0].name == "docs/lebron-james.txt"
    assert all_pages[1].name == "docs/stephen-curry.txt"
    assert all_pages[2].name == "docs/Bill-Russel.txt"
    assert all_pages[3].name == "docs/larry-bird.txt"

def test_get_wiki_page():
    mock_storage_client = MockStorageClient()
    backend_test = Backend(mock_storage_client)
    page = backend_test.get_wiki_page("blob-name")
    assert page.name == "LBJ"

def test_get_metadata():
    mock_storage_client = MockStorageClient()
    backend_test = Backend(mock_storage_client)
    page = backend_test.get_metadata("docs/lebron-james.txt")
    assert page.name == "LBJ"

def test_get_searched_page():
    mock_storage_client = MockStorageClient()
    backend_test = Backend(mock_storage_client)
    page = backend_test.get_searched_pages("james")
    assert backend_test.searched_pages[0].name == "docs/lebron-james.txt"

def test_get_searched_pages():
    mock_storage_client = MockStorageClient()
    backend_test = Backend(mock_storage_client)
    pages = backend_test.get_searched_pages("james")
    assert backend_test.searched_pages[0].name == "docs/lebron-james.txt"
    assert backend_test.searched_pages[1].name == "docs/james-harden.txt"


def test_get_image():
    pass


def test_upload():
    pass

def test_update_player_metadata():
    mock_storage_client = MockStorageClient()
    backend_test = Backend(mock_storage_client, open_mock)
    backend_test.update_player_metadata("test.txt", "center", 2012, ["Test Team"])
    assert backend_test.all_players == {'test.txt': {
        'position': 'center',
        'draft_year': 2012,
        'teams': ['Test Team']
    }}


def test_sort_by_name():
    mock_storage_client = MockStorageClient()
    backend_test = Backend(mock_storage_client)
    backend_test.update_sort_by_name("file-name.txt")
    assert backend_test.pages_by_name['file'] == ['docs/file-name.txt']
    assert backend_test.pages_by_name['name'] == ['docs/file-name.txt']

def test_create_metadata():
    test_file = MockFile("test_file.txt", "")
    mock_storage_client = MockStorageClient()
    backend = Backend(storage_client=mock_storage_client, mock_file=test_file)
    backend.create_metadata("test_file")
    assert backend.metadata_file == "test_file-metadata.txt"
    assert test_file.content == "Number of Vists: 0\n"

