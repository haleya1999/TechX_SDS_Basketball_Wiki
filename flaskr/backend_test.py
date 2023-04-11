from flaskr.backend import Backend

# TODO(Project 1): Write tests for Backend methods.


class MockBlob:

    def __init__(self, username):
        self.name = username

    def __enter__(self):
        return self


class MockBucket:

    def __init__(self):
        pass

    def blob(self, name):
        return "LBJ"

    def image(self, name="test_img"):
        self.name = name
        return "test_img.jpg"


class MockStorageClient:
    """
        mock_storage_client = MockStorageClient()
        backend_test = Backend(mock_storage_client)
        image = "test_img.jpg"
        assert backend_test.get_image(image) == "test_img.jpg"
    """
    def __init__(self):
        pass

    def list_blobs(self, name, prefix=""):
        return ["LeBron James", "Stephen Curry", "Bill Russel", "Larry Bird"]

    def bucket(self, bucket_name):
        mock_bucket = MockBucket()
        return MockBucket()

class MockFile:
    def __init__(self):
        self.content = ""
        self.filename = ""
    
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
    assert page == "LBJ"


def test_get_image():
    pass

def test_upload():
    pass

def test_create_metadata():
    test_file = MockFile()
    def mock_open(filename, _):
        test_file.set_filename(test_file)
        test_file.write("Author: Khloe W.")
        return test_file
    # original_open = open
    # open = mock_open
    mock_storage_client = MockStorageClient()
    backend = Backend(storage_client=mock_storage_client, mock_file=mock_open)
    backend.create_metadata("test_file")
    # open = original_open
    assert test_file.filename == "test_file-metadata.txt"
    assert test_file.content == "Author: Khloe W."
