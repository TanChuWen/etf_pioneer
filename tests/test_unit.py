from app import app
import unittest
from unittest.mock import patch, MagicMock
from utils import generate_wordcloud
from models.news_model import get_news_data
from models.etf_model import get_etf_overview, get_etf_performance, get_top_industry, get_top10_stock


class TestGenerateWordCloud(unittest.TestCase):
    def test_generate_wordcloud(self):
        text = "測試 測試 測試"
        result = generate_wordcloud(text)
        self.assertTrue(result.startswith("data:image/png;base64,"))


class TestGetNewsData(unittest.TestCase):
    @patch('utils.get_db_connection')
    def test_get_news_data(self, mock_get_db_connection):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Define mock return value for the cursor's fetchall method
        mock_cursor.fetchall.return_value = [
            {
                'news_title': '測試新聞1',
                'news_date': '2024-05-04',
                'website': 'test1.com',
                'crawler_date': '2024-05-05',
                'news_link': 'https://test.com/news1'
            },
            {
                'news_title': '測試新聞2',
                'news_date': '2024-05-05',
                'website': 'test2.com',
                'crawler_date': '2024-05-06',
                'news_link': 'https://test.com/news2'
            }
        ]

        # Mock the execute method to not throw any errors
        mock_cursor.execute.return_value = None

        # Call the function to test
        result = get_news_data(mock_conn, '2024-05-04', '2024-05-10')

        # Assertions
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

        self.assertEqual(result[0]['news_title'], '測試新聞1')
        self.assertEqual(result[0]['news_date'], '2024-05-04')
        self.assertEqual(result[0]['website'], 'test1.com')
        self.assertEqual(result[0]['crawler_date'], '2024-05-05')
        self.assertEqual(result[0]['news_link'], 'https://test.com/news1')

        self.assertEqual(result[1]['news_title'], '測試新聞2')
        self.assertEqual(result[1]['news_date'], '2024-05-05')
        self.assertEqual(result[1]['website'], 'test2.com')
        self.assertEqual(result[1]['crawler_date'], '2024-05-06')
        self.assertEqual(result[1]['news_link'], 'https://test.com/news2')


if __name__ == '__main__':
    unittest.main()
