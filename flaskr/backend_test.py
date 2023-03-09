from flaskr.backend import Backend

# TODO(Project 1): Write tests for Backend methods.

class MockStorageClient:
    def __init__(self):
        pass
    def list_blobs(self, name):
        return ["LeBron James", "Stephen Curry", "Bill Russel", "Larry Bird"]

def test_get_all_pages():
    mock_storage_client = MockStorageClient()
    backend_test = Backend(mock_storage_client)
    all_pages = backend_test.get_all_page_names()
    assert all_pages == ["LeBron James", "Stephen Curry", "Bill Russel", "Larry Bird"]