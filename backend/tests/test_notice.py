import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

class TestNotice(unittest.TestCase):

    client = TestClient(app)

    @patch("main.db.read")
    def test_view_notice(self, mock_read):
        response = self.client.get("/api/v1/organisation/619d0966d56a9291379303f0/notices").json()

        mock_read.return_value = {
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

        self.assertEqual(response['message'], "retrieved successfully")

    @patch('main.db.save')
    def test_create_notice(self, mock_save):
        payload = {
            "author_img_url": "http://test.u",
            "author_name": "string",
            "author_username": "string",
            "media": [],
            "message": "string",
            "title": "string",
            "views": "0",
        }
    
        mock_save.return_value = {
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

        response = self.client.post("/api/v1/organisation/619d0966d56a9291379303f0/create", json=payload).json()
        
        self.assertEqual(response["data"]["author_img_url"], "http://test.u")
        self.assertEqual(response["message"], "successfully created")
        self.assertTrue(response["success"])

    @patch("main.db.delete")
    def test_delete_notice(self, mock_delete):
        response = self.client.delete("/api/v1/organisation/619d0966d56a9291379303f0/notices/61898407660aa90fb295e2c1/delete").json()

        mock_delete.return_value = {}

        self.assertEqual(len(response["data"]), 0)
        self.assertEqual(response['message'], "Delete Operation Successful")

    @patch('main.db.update')
    def test_update_notice(self, mock_update):
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

        response = self.client.patch("/api/v1/organisation/619d0966d56a9291379303f0/notices/61898407660aa90fb295e2c1/edit", json=payload).json()
        
        self.assertEqual(response['data']['title'], 'test')
        self.assertEqual(response['message'],"Notice has been successfully updated")