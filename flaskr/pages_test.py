from flaskr import create_app
import os

import pytest


# See https://flask.palletsprojects.com/en/2.2.x/testing/
# for more info on testing
class User:

    def __init__(self, username):
        self.username = username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username


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
    assert b"Basketball Player Wiki" in resp.data


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
def test_pages(client):
    resp = client.get("/pages")
    assert resp.status_code == 200
    assert b"All Pages" in resp.data


def test_get_page(client):
    resp = client.get("/pages/docs/kareem-abdul-jabbar.txt")
    assert resp.status_code == 200
    assert b"Kareem Abdul-Jabbar" in resp.data


def test_edit_page(client):
    get = client.get("/pages/docs/kareem-abdul-jabbar.txt/edit")
    assert get.status_code == 200
    assert b"Editing" in get.data
