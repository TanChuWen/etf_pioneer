import unittest
from unittest.mock import patch, MagicMock
from app import app
from bs4 import BeautifulSoup


class TestETFTop10Stocks(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()  # 設置 Flask 測試客戶端
        self.app.testing = True      # 啟用測試模式

    @patch('pymysql.connect')  # 模擬 pymysql.connect 函數
    def test_search_results(self, mock_connect):
        # 配置 mock 對象
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        # 模擬 cursor 對象
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor

        # 配置 fetchone 和 fetchall 的 side_effect
        def mock_fetchone(*args):
            if "FROM etf_overview_data" in args[0]:
                return {'etf_name': '元大台灣50', 'symbol': '0050', 'price_today': 100, 'up_down_change': 1, 'up_down_percentage': 1.0, 'data_updated_date': '2023-06-01'}
            elif "FROM etf_performance" in args[0]:
                return {'symbol': '0050', '1_week': 1.5, '1_month': 2.0, '3_month': 3.5, '6_month': 4.0, 'YTD': 5.0, '1_year': 6.0, '2_year': 7.0, '3_year': 8.0, '5_year': 9.0, '10_year': 10.0, 'data_updated_date': '2023-06-01'}
            elif "SUM(ratio)" in args[0]:
                return {'total_ratio': 30}
            return None

        def mock_fetchall(*args):
            if "FROM top_industry" in args[0]:
                return [
                    {'symbol': '0050', 'industry': 'Technology',
                        'ratio': 20, 'data_updated_date': '2023-06-01'},
                    {'symbol': '0050', 'industry': 'Healthcare',
                        'ratio': 10, 'data_updated_date': '2023-06-01'}
                ]
            elif "FROM top10_stock" in args[0]:
                return [
                    {'symbol': '0050', 'ranking': 1, 'stock_name': 'TSMC',
                        'ratio': 10, 'data_updated_date': '2023-06-01'},
                    {'symbol': '0050', 'ranking': 2, 'stock_name': 'Foxconn',
                        'ratio': 5, 'data_updated_date': '2023-06-01'}
                ]
            return []

        # 設置 cursor 的 fetchone 和 fetchall 的 side_effect
        mock_cursor.fetchone.side_effect = mock_fetchone
        mock_cursor.fetchall.side_effect = mock_fetchall

        # 發送 HTTP GET 請求到 /search-results?symbol=0050
        response = self.app.get('/search-results?symbol=0050')
        assert response.status_code == 200  # 確認 HTTP 響應狀態碼為 200

        # 解析 HTML 內容
        html_content = response.data.decode('utf-8')
        soup = BeautifulSoup(html_content, 'html.parser')

        # 確認頁面上存在 ETF 的名稱
        etf_name_element = soup.find('h1')  # 查找 HTML 中的 <h1> 標籤
        assert etf_name_element is not None  # 確認 <h1> 標籤存在
        assert '元大台灣50' in etf_name_element.text  # 確認 <h1> 標籤的文本中包含 '元大台灣50'


if __name__ == '__main__':
    unittest.main()  # 運行測試


# import unittest
# from unittest.mock import patch, MagicMock
# from app import app
# from bs4 import BeautifulSoup


# class TestETFTop10Stocks(unittest.TestCase):
#     def setUp(self):
#         self.app = app.test_client()
#         self.app.testing = True

#     @patch('pymysql.connect')
#     def test_search_results(self, mock_connect):
#         # 配置 mock 對象
#         mock_connection = MagicMock()
#         mock_connect.return_value = mock_connection

#         # 模擬 cursor 對象
#         mock_cursor = MagicMock()
#         mock_connection.cursor.return_value = mock_cursor

#         # 假設你的應用在查詢數據庫時返回的數據是這樣的
#         # 這裡設置 cursor 執行 SQL 查詢時的返回值
#         mock_cursor.fetchall.return_value = [
#             {'symbol': '0050', 'name': '元大台灣50'}
#         ]

#         # 發送 HTTP GET 請求到 /search-results?symbol=0050
#         response = self.app.get('/search-results?symbol=0050')
#         assert response.status_code == 200

#         # 解析 HTML 內容
#         html_content = response.data.decode('utf-8')
#         soup = BeautifulSoup(html_content, 'html.parser')

#         # 確認頁面上存在 ETF 的名稱
#         etf_name_element = soup.find('h1')
#         assert etf_name_element is not None
#         assert '元大台灣50' in etf_name_element.text


# if __name__ == '__main__':
#     unittest.main()


# # from app import app
# # import unittest
# # from app import app
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
