from flaskr.backend import Backend
from collections import defaultdict

# TODO(Project 1): Write tests for Backend methods.


class MockBlob:

    def __init__(self):
        self.name = "LBJ"

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

    def write(self, contents):
        pass

    def upload_from_filename(self, filename, if_generation_match):
        pass


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



class MockFile:
    def __init__(self, filename, param) :
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

def test_upload():
    pass

def test_create_metadata():
    test_file = MockFile("test_file.txt", "")
    mock_storage_client = MockStorageClient()
    backend = Backend(storage_client=mock_storage_client, mock_file=test_file)
    backend.create_metadata("test_file")
    assert backend.metadata_file == "test_file-metadata.txt"
    assert test_file.content == "Number of Vists: 0\n"
