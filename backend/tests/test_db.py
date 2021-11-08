from fastapi.testclient import TestClient

from main import app
from storage.db import db

client = TestClient(app)


def test_read():
    notice_sample_data = {
        "_id": "61898407660aa90fb295e2c1",
        "author_img_url": "http://test.u",
        "author_name": "string",
        "author_username": "string",
        "created": "2021-11-08 13:35:58.893000+00:00",
        "media": [],
        "message": "string",
        "title": "string",
        "views": "0",
    }
    response = db.read("noticeboard", org_id="61767acbbc003777d000a92a")
    assert response["status"] == 200
    notices = response["data"]

    assert notices[0] == notice_sample_data

def test_view_notices():
    notice_sample_data = {
        "_id": "61898407660aa90fb295e2c1",
        "author_img_url": "http://test.u",
        "author_name": "string",
        "author_username": "string",
        "created": "2021-11-08 13:35:58.893000+00:00",
        "media": [],
        "message": "string",
        "title": "string",
        "views": "0",
    }
    response = client.get("/api/v1/organisation/61767acbbc003777d000a92a/notices")
    assert response.status_code == 200
    response_data = response.json()
    notices = response_data["data"]
    reversed_list = notices[::-1]

    assert reversed_list[0] == notice_sample_data

# def test_create_notice():
#     db.save()
