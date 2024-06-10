import unittest
from unittest.mock import patch, MagicMock
from app import app  # Import your Flask app instance

# Mock functions based on provided test data


def mock_get_etf_overview(*args, **kwargs):
    return {
        'etf_name': '元大台灣50',
        'symbol': '0050',
        'price_today': 168.45,
        'up_down_change': '1.59',
        'up_down_percentage': '0.96%',
        'data_updated_date': '2024/06/05 14:30'
    }


def mock_get_etf_performance(*args, **kwargs):
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


def mock_get_top_industry(*args, **kwargs):
    return [
        {'symbol': '0050', 'industry': '其他電子業',
            'ratio': '5.00%', 'data_updated_date': '2024/06/01'},
        {'symbol': '0050', 'industry': '半導體業', 'ratio': '62.15%',
            'data_updated_date': '2024/06/01'},
        # Other industries...
    ]


def mock_get_top10_stock(*args, **kwargs):
    return [
        {'symbol': '0050', 'ranking': 1, 'stock_name': '台積電',
            'ratio': '52.19%', 'data_updated_date': '2024/04/01'},
        # Other stocks...
    ]

# Mock for the database connection


def mock_get_db_connection():
    # Create a mock connection object
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = MagicMock()
    return mock_conn


class TestFlaskApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('models.etf_model.get_etf_overview', side_effect=mock_get_etf_overview)
    @patch('models.etf_model.get_etf_performance', side_effect=mock_get_etf_performance)
    @patch('models.etf_model.get_top_industry', side_effect=mock_get_top_industry)
    @patch('models.etf_model.get_top10_stock', side_effect=mock_get_top10_stock)
    @patch('utils.get_db_connection', side_effect=mock_get_db_connection)
    def test_search_results_with_data(self, mock_db, mock_overview, mock_performance, mock_industry, mock_stock):
        # Send GET request to the application
        response = self.app.get('/search-results?symbol=0050')

        # Check HTTP status code
        self.assertEqual(response.status_code, 200)

        # Check HTML content for specific ETF details
        html_content = response.data.decode('utf-8')

        # Print the HTML content for debugging
        print(html_content)

        # Verify that the expected data is present in the response HTML
        self.assertIn('元大台灣50', html_content)  # ETF name
        self.assertIn('168.45', html_content)  # Price Today
        self.assertIn('1.59', html_content)  # Up Down Change
        self.assertIn('0.96%', html_content)  # Up Down Percentage
        self.assertIn('2024/06/05 14:30', html_content)  # Data Updated Date

        # Check if performance data is present
        self.assertIn('36.94%', html_content)  # 1 Year Performance
        self.assertIn('25.57%', html_content)  # YTD Performance


if __name__ == '__main__':
    unittest.main()
