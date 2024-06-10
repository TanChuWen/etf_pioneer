# test_app.py
import unittest
from unittest.mock import patch, MagicMock
from app import app


class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('pymysql.connect')  # 模擬 pymysql.connect 函數
    def test_search_results_with_data(self, mock_connect):
        # 配置 mock 對象
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        # 模擬 cursor 對象
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # 配置 fetchone 和 fetchall 的 side_effect
        def mock_fetchone(*args):
            query = args[0]
            if "FROM etf_overview_data" in query:
                return {'etf_name': '元大台灣50', 'symbol': '0050', 'price_today': 100, 'up_down_change': 1, 'up_down_percentage': 1.0, 'data_updated_date': '2023-06-01'}
            elif "FROM etf_performance" in query:
                return {'symbol': '0050', '1_week': 1.5, '1_month': 2.0, '3_month': 3.5, '6_month': 4.0, 'YTD': 5.0, '1_year': 6.0, '2_year': 7.0, '3_year': 8.0, '5_year': 9.0, '10_year': 10.0, 'data_updated_date': '2023-06-01'}
            elif "SUM(ratio)" in query:
                return {'total_ratio': 30}  # 用於計算 top_industry 的其他比率
            return None

        def mock_fetchall(*args):
            query = args[0]
            if "FROM top_industry" in query:
                return [
                    {'symbol': '0050', 'industry': 'Technology',
                        'ratio': 20, 'data_updated_date': '2023-06-01'},
                    {'symbol': '0050', 'industry': 'Healthcare',
                        'ratio': 10, 'data_updated_date': '2023-06-01'}
                ]
            elif "FROM top10_stock" in query:
                return [
                    {'symbol': '0050', 'ranking': 1, 'stock_name': 'TSMC',
                        'ratio': 10, 'data_updated_date': '2023-06-01'},
                    {'symbol': '0050', 'ranking': 2, 'stock_name': 'Foxconn',
                        'ratio': 5, 'data_updated_date': '2023-06-01'}
                ]
            return []

        # 設置 side_effect
        mock_cursor.fetchone.side_effect = mock_fetchone
        mock_cursor.fetchall.side_effect = mock_fetchall

        # 發送 GET 請求到 /search-results?symbol=0050
        response = self.app.get('/search-results?symbol=0050')

        # 檢查 HTTP 響應狀態碼
        self.assertEqual(response.status_code, 200)

        # 檢查返回的 HTML 內容
        html_content = response.data.decode('utf-8')
        print(html_content)
        self.assertIn('元大台灣50', html_content)  # 檢查 ETF 名稱
        self.assertIn('Technology', html_content)  # 檢查行業數據
        self.assertIn('TSMC', html_content)        # 檢查前十大持股
        # self.assertIn('10年', html_content)        # 檢查 10 年的表現數據

    @patch('pymysql.connect')  # 模擬 pymysql.connect 函數
    def test_search_results_no_data(self, mock_connect):
        # 配置 mock 對象
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        # 模擬 cursor 對象
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        # 配置 cursor 的 fetchone 和 fetchall 返回 None 或空數據
        mock_cursor.fetchone.side_effect = [None, None, None]
        mock_cursor.fetchall.side_effect = [[], []]

        # 發送 GET 請求到 /search-results?symbol=unknown
        response = self.app.get('/search-results?symbol=unknown')

        # 檢查 HTTP 響應狀態碼
        self.assertEqual(response.status_code, 200)

        # 檢查返回的 HTML 內容，確保顯示沒有數據的消息
        html_content = response.data.decode('utf-8')
        self.assertIn('No data found', html_content)


if __name__ == '__main__':
    unittest.main()


# # from app import app
# # import unittest
# # from bs4 import BeautifulSoup


# # class TestETFTop10Stocks(unittest.TestCase):
# #     def setUp(self):
# #         self.app = app.test_client()
# #         self.app.testing = True

# #     def test_search_results(self):
# #         response = self.app.get('/search-results?symbol=0050')
# #         assert response.status_code == 200

# #         html_content = response.data.decode('utf-8')
# #         soup = BeautifulSoup(html_content, 'html.parser')

# #         # Verify 'etf_overview_data' rendering
# #         etf_name_element = soup.find('h1')
# #         assert etf_name_element is not None
# #         # Assuming '元大台灣50' is part of the etf_overview_data
# #         assert '元大台灣50' in etf_name_element.text


# # if __name__ == '__main__':
# #     unittest.main()
