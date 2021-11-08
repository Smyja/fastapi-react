# import pytest
import requests.exceptions
import responses
import unittest
import unittest.mock as mock

# from storage.db import db
from requests.exceptions import HTTPError
from main import app

print(app)

