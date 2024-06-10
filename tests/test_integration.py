import unittest
from unittest.mock import patch, MagicMock
from app import app  # Import your Flask app instance

# Define your mock functions


def mock_get_db_connection():
    # Mock the database connection and cursor
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    return mock_connection


def mock_get_etf_overview(connection, symbol):
    if symbol == "0050":
        return {
            "etf_name": "元大台灣50",
            "symbol": "0050",
            "price_today": 168.45,
            "up_down_change": "1.59",
            "up_down_percentage": "0.96%",
            "data_updated_date": "2024/06/05 14:30"
        }
    return None


def mock_get_etf_performance(connection, symbol):
    if symbol == "0050":
        return {
            "symbol": "0050",
            "1_week": "-3.04%",
            "1_month": "6.30%",
            "3_month": "13.17%",
            "6_month": "30.17%",
            "YTD": "25.57%",
            "1_year": "36.94%",
            "2_year": "17.84%",
            "3_year": "9.88%",
            "5_year": "20.12%",
            "10_year": "13.70%",
            "data_updated_date": "2024/06/04"
        }
    return None


def mock_get_top_industry(connection, symbol):
    if symbol == "0050":
        return [
            {"symbol": "0050", "industry": "其他電子業",
                "ratio": "5.00%", "data_updated_date": "2024/06/01"},
            {"symbol": "0050", "industry": "其餘行業 - 光電業",
                "ratio": "0.61%", "data_updated_date": "2024/06/01"},
            {"symbol": "0050", "industry": "其餘行業 - 其他",
                "ratio": "0.34%", "data_updated_date": "2024/06/01"},
            {"symbol": "0050", "industry": "其餘行業 - 塑膠工業",
                "ratio": "1.84%", "data_updated_date": "2024/06/01"},
            {"symbol": "0050", "industry": "其餘行業 - 水泥工業",
                "ratio": "0.57%", "data_updated_date": "2024/06/01"},
            {"symbol": "0050", "industry": "其餘行業 - 汽車工業",
                "ratio": "0.53%", "data_updated_date": "2024/06/01"},
            {"symbol": "0050", "industry": "其餘行業 - 油電燃氣業",
                "ratio": "0.24%", "data_updated_date": "2024/06/01"},
            {"symbol": "0050", "industry": "其餘行業 - 航運業",
                "ratio": "0.56%", "data_updated_date": "2024/06/01"},
            {"symbol": "0050", "industry": "其餘行業 - 貿易百貨",
                "ratio": "0.40%", "data_updated_date": "2024/06/01"},
            {"symbol": "0050", "industry": "其餘行業 - 通信網路業",
                "ratio": "2.88%", "data_updated_date": "2024/06/01"},
            {"symbol": "0050", "industry": "其餘行業 - 鋼鐵工業",
                "ratio": "0.77%", "data_updated_date": "2024/06/01"},
            {"symbol": "0050", "industry": "其餘行業 - 電機機械",
                "ratio": "0.36%", "data_updated_date": "2024/06/01"},
            {"symbol": "0050", "industry": "其餘行業 - 食品工業",
                "ratio": "1.01%", "data_updated_date": "2024/06/01"},
            {"symbol": "0050", "industry": "半導體業", "ratio": "62.15%",
                "data_updated_date": "2024/06/01"},
            {"symbol": "0050", "industry": "金融保險", "ratio": "12.65%",
                "data_updated_date": "2024/06/01"},
            {"symbol": "0050", "industry": "電子零組件業",
                "ratio": "3.15%", "data_updated_date": "2024/06/01"},
            {"symbol": "0050", "industry": "電腦及週邊設備業",
                "ratio": "5.87%", "data_updated_date": "2024/06/01"},
            {"symbol": "0050", "industry": "其他", "ratio": "1.07%",
                "data_updated_date": "2024/06/01"}
        ]
    return []


def mock_get_top10_stock(connection, symbol):
    if symbol == "0050":
        return [
            {"symbol": "0050", "ranking": 1, "stock_name": "台積電",
                "ratio": "52.19%", "data_updated_date": "2024/04/01"},
            {"symbol": "0050", "ranking": 2, "stock_name": "鴻海",
                "ratio": "4.74%", "data_updated_date": "2024/04/01"},
            {"symbol": "0050", "ranking": 3, "stock_name": "聯發科",
                "ratio": "4.06%", "data_updated_date": "2024/04/01"},
            {"symbol": "0050", "ranking": 4, "stock_name": "廣達",
                "ratio": "1.90%", "data_updated_date": "2024/04/01"},
            {"symbol": "0050", "ranking": 5, "stock_name": "台達電",
                "ratio": "1.90%", "data_updated_date": "2024/04/01"},
            {"symbol": "0050", "ranking": 6, "stock_name": "中信金",
                "ratio": "1.71%", "data_updated_date": "2024/04/01"},
            {"symbol": "0050", "ranking": 7, "stock_name": "聯電",
                "ratio": "1.64%", "data_updated_date": "2024/04/01"},
            {"symbol": "0050", "ranking": 8, "stock_name": "富邦金",
                "ratio": "1.47%", "data_updated_date": "2024/04/01"},
            {"symbol": "0050", "ranking": 9, "stock_name": "日月光投控",
                "ratio": "1.39%", "data_updated_date": "2024/04/01"},
            {"symbol": "0050", "ranking": 10, "stock_name": "中華電",
                "ratio": "1.30%", "data_updated_date": "2024/04/01"},
            {"symbol": "0050", "ranking": "其他", "stock_name": "其他",
                "ratio": "27.70%", "data_updated_date": "2024/04/01"}
        ]
    return []


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

        # Check if industry data is present
        # self.assertIn('半導體業', html_content)  # Industry

        # Check if top stock data is present
        # self.assertIn('台積電', html_content)  # Top Stock Name


if __name__ == '__main__':
    unittest.main()
