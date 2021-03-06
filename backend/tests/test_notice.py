import pytest
from fastapi.testclient import TestClient
from unittest import mock
from main import app


client = TestClient(app)

@pytest.mark.dbsa
@mock.patch(client.view_notice)
def test_view_notice(mock_read):
    mock_read.return_value.status_code=200
    response = client.get("/api/v1/organisation/61767acbbc003777d000a92a/notices")
    
    print(response)
    assert response.status_code == 200

@mock.patch('main.db.save')
def test_create_notice(mock_save):
    payload = {
        "author_img_url": "http://tomat.u",
        "author_name": "string",
        "author_username": "string",
        "media": [],
        "message": "string",
        "title": "string",
        "views": "0",
    }

    response = client.post("/api/v1/organisation/619d0966d56a9291379303f0/create", json=payload).json()
    print(response)
    
    assert response["data"]["author_img_url"] == "http://tomat.u"
    assert response["message"] == "successfully created"
    assert (response["success"]) == True



@mock.patch('main.db.update')
def test_update_notice(mock_update):
    payload = {
        "title": "test",
    }

    mock_update.return_value = {
        "_id": "61898407660aa90fb295e2c1",
        "author_img_url": "http://test.u",
        "author_name": "string",
        "author_username": "string",
        "created": "2021-11-08 13:35:58.893000+00:00",
        "media": [],
        "message": "string",
        "title": "test",
        "views": "0",
    }

    response = client.patch("/api/v1/organisation/619d0966d56a9291379303f0/notices/61898407660aa90fb295e2c1/edit", json=payload).json()
    
    assert response['data']['title'] == 'test'
    assert response['message'] == "Notice has been successfully updated"


@mock.patch("main.db.delete")
def test_delete_notice(mock_delete):
    response = client.delete("/api/v1/organisation/619d0966d56a9291379303f0/notices/619de595d56a92913793041c/delete").json()

    mock_delete.return_value = {}

    assert response['message'] == "Delete Operation Successful"
