from app import app
import unittest
from bs4 import BeautifulSoup


class TestETFTop10Stocks(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_search_results(self):
        response = self.app.get('/search-results?symbol=0050')
        assert response.status_code == 200

        html_content = response.data.decode('utf-8')
        soup = BeautifulSoup(html_content, 'html.parser')

        # Verify 'etf_overview_data' rendering
        etf_name_element = soup.find('h1')
        assert etf_name_element is not None
        # Assuming '元大台灣50' is part of the etf_overview_data
        assert '元大台灣50' in etf_name_element.text


if __name__ == '__main__':
    unittest.main()
