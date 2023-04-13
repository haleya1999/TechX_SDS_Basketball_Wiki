from flaskr.backend import Backend

# TODO(Project 1): Write tests for Backend methods.


class MockBlob:

    def __init__(self):
        self.name = "LBJ"

    def __enter__(self):
        return self
    
    def open(self, param):
        if param == "r":
            return
        if param == "w":
            return            



class MockBucket:

    def __init__(self):
        pass

    def blob(self, name):
        return MockBlob()

    def image(self, name="test_img"):
        self.name = name
        return "test_img.jpg"


class MockStorageClient:

    def __init__(self):
        pass

    def list_blobs(self, name, prefix=""):
        return ["LeBron James", "Stephen Curry", "Bill Russel", "Larry Bird"]

    def bucket(self, bucket_name):
        mock_bucket = MockBucket()
        return MockBucket()


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

def test_add_to_dict():
    mock_storage_client = MockStorageClient()
    backend_test = Backend(mock_storage_client)
    backend_test.add_to_dict("test.txt", "center", 2012, ["Test Team"])
    assert backend_test.all_players == {'test.txt': {
        'position': 'center',
        'draft_year': 2012,
        'teams': ['Test Team']
    }}

