from flaskr.backend import Backend

# TODO(Project 1): Write tests for Backend methods.
class MockBucket:
    def __init__(self):
        pass
    def blob(self, name):
        return "LBJ"
        
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
    assert all_pages == ["LeBron James", "Stephen Curry", "Bill Russel", "Larry Bird"]
def test_get_wiki_page():
    mock_storage_client = MockStorageClient()
    backend_test = Backend(mock_storage_client)
    page = backend_test.get_wiki_page("blob-name")
    assert page == "LBJ"