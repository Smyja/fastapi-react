from fastapi.testclient import TestClient

from main import app
from storage.db import db
from .json import notice_sample_data

client = TestClient(app)


def test_read():
    response = db.read("noticeboard", org_id="61767acbbc003777d000a92a")
    notices = response["data"]
    assert response["status"] == 200
    assert notices[0] == notice_sample_data


def test_view_notices():
    response = client.get("/api/v1/organisation/61767acbbc003777d000a92a/notices")
    response_data = response.json()
    notices = response_data["data"]
    reversed_list = notices[::-1]
    assert response.status_code == 200
    assert reversed_list[0] == notice_sample_data


# def test_create_notice():
#     db.save()
