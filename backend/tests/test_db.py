import pytest
import requests.exceptions
import responses
import unittest
import unittest.mock as mock

from storage.db import db
from requests.exceptions import HTTPError
class TestWrapper(unittest.TestCase):
    def test_save(self):
        # Arrange
        coins_json_sample = {"bitcoin": {"usd": 7984.89}}

        responses.add(responses.GET, 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
                          json = coins_json_sample, status = 200)

        # Act
        response = CoinGeckoAPI().get_price('bitcoin', 'usd')

        ## Assert
        assert response == coins_json_sample
        tolu = dict(store="mama_put", owner="Aunty justina")
        tolu.update(iphone=5)

# e=Db.save("not6", notice_data=tolu)

