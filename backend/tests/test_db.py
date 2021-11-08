from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_create_notie():
    response = client.get("/api/v1/organisation/61767acbbc003777d000a92a/notices")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
