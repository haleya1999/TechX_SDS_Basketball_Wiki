from flaskr.backend import Backend
import pytest


class MockBucket:
    def __init__(self):
        pass
    def blob(self, name):
        return "LBJ"
    def get_blob(self, username):
        blobs = ["LeBron James", "Stephen Curry", "Bill Russel", "Larry Bird"]
        for name in blobs:
            if username == name:
                return True
        return False
    
        
class MockStorageClient:
    def __init__(self):
        pass
    def list_blobs(self, name, prefix=""):
        return ["LeBron James", "Stephen Curry", "Bill Russel", "Larry Bird"]
    def bucket(self, bucket_name):
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
