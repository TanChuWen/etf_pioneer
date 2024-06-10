from unittest import TestCase
from unittest.mock import patch
from app import app  # Assuming 'app' is your Flask instance

# Mock data functions


def mock_get_etf_overview(symbol):
    return {
        'etf_name': '元大台灣50',
        'symbol': '0050',
        'price_today': 168.45,
        'up_down_change': '1.59',
        'up_down_percentage': '0.96%',
        'data_updated_date': '2024/06/05 14:30'
    }


def mock_get_etf_performance(symbol):
    return {
        'symbol': '0050',
        '1_week': '-3.04%',
        '1_month': '6.30%',
        '3_month': '13.17%',
        '6_month': '30.17%',
        'YTD': '25.57%',
        '1_year': '36.94%',
        '2_year': '17.84%',
        '3_year': '9.88%',
        '5_year': '20.12%',
        '10_year': '13.70%',
        'data_updated_date': '2024/06/04'
    }


def mock_get_top_industry(symbol):
    return [
        {'symbol': '0050', 'industry': '半導體業', 'ratio': '62.15%',
            'data_updated_date': '2024/06/01'},
        # More industries can be added here
    ]


def mock_get_top10_stock(symbol):
    return [
        {'symbol': '0050', 'ranking': 1, 'stock_name': '台積電',
            'ratio': '52.19%', 'data_updated_date': '2024/04/01'},
        # More stocks can be added here
    ]

# Integration test class


class TestFlaskApp(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()
        cls.app.testing = True

    @patch('models.etf_model.get_etf_overview', side_effect=mock_get_etf_overview)
    @patch('models.etf_model.get_etf_performance', side_effect=mock_get_etf_performance)
    @patch('models.etf_model.get_top_industry', side_effect=mock_get_top_industry)
    @patch('models.etf_model.get_top10_stock', side_effect=mock_get_top10_stock)
    # Mocking DB connection
    @patch('utils.get_db_connection', side_effect=lambda: None)
    def test_search_results_with_data(self, mock_db, mock_overview, mock_performance, mock_industry, mock_stock):
        response = self.app.get('/search-results?symbol=0050')
        self.assertEqual(response.status_code, 200)

        html_content = response.data.decode('utf-8')
        print(html_content)

        # Check for expected values in HTML content
        self.assertIn('元大台灣50', html_content)
        self.assertIn('168.45', html_content)
        self.assertIn('1.59', html_content)
        self.assertIn('0.96%', html_content)
        self.assertIn('2024/06/05 14:30', html_content)
        self.assertIn('36.94%', html_content)
        self.assertIn('25.57%', html_content)
        # self.assertIn('半導體業', html_content)
        # self.assertIn('台積電', html_content)
