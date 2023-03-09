from flaskr import create_app
import os

import pytest

# See https://flask.palletsprojects.com/en/2.2.x/testing/ 
# for more info on testing
@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

# TODO(Checkpoint (groups of 4 only) Requirement 4): Change test to
# match the changes made in the other Checkpoint Requirements.
def test_home_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Hello, World!\n" in resp.data

def test_about_page(client):
    get = client.get("/about")
    assert get.status_code == 200
    assert b"This is a wiki exclusively about basketball players" in get.data
    assert b"wiki-contents/pictures" in get.data

def test_upload_page(client):
    get = client.get("/upload")
    assert get.status_code == 200
    assert b"Upload a Doc to the Wiki" in get.data
    post = client.post("/upload")
    assert post.status_code == 302
# TODO(Project 1): Write tests for other routes.
