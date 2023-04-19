from flaskr.backend import Backend

# TODO(Project 1): Write tests for Backend methods.


class MockBlob:

    def __init__(self, username):
        self.name = username

    def __enter__(self):
        return self

    def name(self):
        return self.name


class MockBucket:

    def __init__(self):
        pass

    def blob(self, name):
        return "LBJ"

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
    assert page == "LBJ"


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
