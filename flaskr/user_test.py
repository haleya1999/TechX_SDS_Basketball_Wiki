from flaskr.backend import Backend
import pytest


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

@pytest.fixture
def test_sign_up():
    mock_storage_client = MockStorageClient()
    backend_test = Backend(mock_storage_client)
    assert backend_test.sign_up("Lebron James", "password") == True