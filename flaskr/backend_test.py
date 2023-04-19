import pytest
import pickle
from flaskr.backend import Backend
from collections import defaultdict
from unittest.mock import MagicMock, patch, Mock, mock_open

# TODO(Project 1): Write tests for Backend methods.


class MockBlob:

    def __init__(self):
        self.name = "LBJ"

    def __enter__(self):
        return self
    
    def __exit__(self, _1, _2, _3):
        pass

    def open(self, param, update=False):
        if update:
            pickle.load
        return self          

    def read(self, _):
        return bytes()

    def readline(self):
        return bytes()

    def write(self, contents):
        pass



    def name(self):
        return self.name


class MockBucket:

    def __init__(self):
        self.blobs = defaultdict(MockBlob)

    def blob(self, name):
        return self.blobs[name]

    def image(self, name="test_img"):
        self.name = name
        return "test_img.jpg"


class MockStorageClient:

    def __init__(self):
        self.bucket = defaultdict(MockBucket)

    def list_blobs(self, name, prefix=""):
        return ["LeBron James", "Stephen Curry", "Bill Russel", "Larry Bird"]
    
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


def test_get_all_pages():
    mock_storage_client = MockStorageClient()
    backend_test = Backend(mock_storage_client)
    all_pages = backend_test.get_all_page_names()
    assert all_pages == [
        "LeBron James", "Stephen Curry", "Bill Russel", "Larry Bird"
    ]


def test_get_wiki_page():
    mock_storage_client = MockStorageClient()
    backend_test = Backend(mock_storage_client)
    page = backend_test.get_wiki_page("blob-name")
    assert page.name == "LBJ"


def test_get_image():
    pass


"""
    mock_storage_client = MockStorageClient()
    backend_test = Backend(mock_storage_client)
    image = "test_img.jpg"
    assert backend_test.get_image(image) == "test_img.jpg"
"""


def test_upload():
    pass


def test_update_player_metadata():
    mock_storage_client = MockStorageClient()
    backend_test = Backend(mock_storage_client, open_mock)
    backend_test.update_player_metadata("test.txt", "center", 2012, ["Test Team"])
    expected = {'test.txt': {
        'position': 'center',
        'draft_year': 2012,
        'teams': ['Test Team']
    }}
    blob = mock_storage_client.bucket['wiki-contents'].blob('test.txt')
    assert backend_test.all_players == expected


def test_sort_by_name():
    mock_storage_client = MockStorageClient()
    backend_test = Backend(mock_storage_client)
    backend_test.update_sort_by_name("file-name.txt")
    assert backend_test.pages_by_name == {
        'file': ['docs/file-name.txt'],
        'name': ['docs/file-name.txt']
    }


def test_fill_names():
    mock_storage_client = mockstorage()
    backend_test = Backend(mock_storage_client)
    backend_test.fill_sort_by_name()
    assert backend_test.pages_by_name == {
        'file': ['docs/test-file.txt', 'docs/file-name.txt'],
        'test': ['docs/test-file.txt'],
        'name': ['docs/file-name.txt']
    }

