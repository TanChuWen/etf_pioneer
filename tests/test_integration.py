import unittest
from unittest.mock import patch, MagicMock
from app import app
from bs4 import BeautifulSoup


class TestETFTop10Stocks(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('pymysql.connect')
    def test_search_results(self, mock_connect):
        # 配置 mock 對象
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        # 模擬 cursor 對象
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor

        # 假設你的應用在查詢數據庫時返回的數據是這樣的
        # 這裡設置 cursor 執行 SQL 查詢時的返回值
        mock_cursor.fetchall.return_value = [
            {'symbol': '0050', 'name': '元大台灣50'}
        ]

        # 發送 HTTP GET 請求到 /search-results?symbol=0050
        response = self.app.get('/search-results?symbol=0050')
        assert response.status_code == 200

        # 解析 HTML 內容
        html_content = response.data.decode('utf-8')
        soup = BeautifulSoup(html_content, 'html.parser')

        # 確認頁面上存在 ETF 的名稱
        etf_name_element = soup.find('h1')
        assert etf_name_element is not None
        assert '元大台灣50' in etf_name_element.text


if __name__ == '__main__':
    unittest.main()


# from app import app
# import unittest
# from app import app
# from bs4 import BeautifulSoup


# class TestETFTop10Stocks(unittest.TestCase):
#     def setUp(self):
#         self.app = app.test_client()
#         self.app.testing = True

#     def test_search_results(self):
#         response = self.app.get('/search-results?symbol=0050')
#         assert response.status_code == 200

#         html_content = response.data.decode('utf-8')
#         soup = BeautifulSoup(html_content, 'html.parser')

#         # Verify 'etf_overview_data' rendering
#         etf_name_element = soup.find('h1')
#         assert etf_name_element is not None
#         # Assuming '元大台灣50' is part of the etf_overview_data
#         assert '元大台灣50' in etf_name_element.text


# if __name__ == '__main__':
#     unittest.main()
