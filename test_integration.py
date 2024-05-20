import unittest
from app import app


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('ETF 排行總覽', response.get_data(as_text=True))

    def test_get_news_data(self):
        response = self.app.get('/etf-pioneer/api/news-wordcloud')
        self.assertEqual(response.status_code, 200)
        self.assertIn('新聞關鍵字文字雲', response.get_data(as_text=True))

    def test_search_results(self):
        response = self.app.get('/search-results?symbol=0050')
        self.assertEqual(response.status_code, 200)
        self.assertIn('與前一個交易日價格差距:', response.get_data(as_text=True))

    def test_search_etf_by_stock(self):
        response = self.app.get(
            '/etf-pioneer/api/stock-to-etf?stock_code=2330')
        self.assertEqual(response.status_code, 200)
        self.assertIn('股票', response.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
