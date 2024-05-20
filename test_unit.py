import unittest
from utils import get_db_connection, fetch_data, fetch_single_record, generate_wordcloud
from models.news_model import get_news_data
from models.etf_model import get_etf_overview, get_etf_performance, get_top_industry, get_top10_stock

# TestDatabaseConnection class inherits from unittest.TestCase
# It aims to test the get_db_connection function


class TestDatabaseConnection(unittest.TestCase):
    def test_get_db_connection(self):
        try:
            conn = get_db_connection()
            self.assertIsNotNone(conn)
            conn.close()
        except Exception as e:
            self.fail(f"Database connection failed: {e}")

# TestFetchData aims to test the fetch_data function


class TestFetchData(unittest.TestCase):
    def test_fetch_data(self):
        try:
            conn = get_db_connection()
            query = "SELECT * FROM etf_ranking_volume LIMIT 1"
            result = fetch_data(conn, query)
            self.assertIsNotNone(result)
            self.assertIsInstance(result, list)
            conn.close()
        except Exception as e:
            self.fail(f"Fetch Data failed: {e}")

# TestFetchSingleRecord aims to test the fetch_single_record function


class TestFetchSingleRecord(unittest.TestCase):
    def test_fetch_single_record(self):
        try:
            conn = get_db_connection()
            query = "SELECT * FROM etf_ranking_volume LIMIT 1"
            result = fetch_single_record(conn, query)
            self.assertIsNotNone(result)
            self.assertIsInstance(result, dict)
            conn.close()
        except Exception as e:
            self.fail(f"Fetch Single Record failed: {e}")


# TestGenerateWordCloud aims to test the generate_wordcloud function


class TestGenerateWordCloud(unittest.TestCase):
    def test_generate_wordcloud(self):
        text = "測試 測試 測試"
        result = generate_wordcloud(text)
        self.assertTrue(result.startswith("data:image/png;base64,"))

# TestGetNewsData aims to test the get_news_data function


class TestGetNewsData(unittest.TestCase):
    def test_get_news_data(self):
        try:
            conn = get_db_connection()
            start_date = "2024-05-04"
            end_date = "2024-05-10"
            result = get_news_data(conn, start_date, end_date)
            self.assertIsNotNone(result)
            self.assertIsInstance(result, list)
            conn.close()
        except Exception as e:
            self.fail(f"Get News Data failed: {e}")

# TestGetETFOverview aims to test the get_etf_overview function


class TestGetETFOverview(unittest.TestCase):
    def test_get_etf_overview(self):
        try:
            conn = get_db_connection()
            symbol = "0050"
            result = get_etf_overview(conn, symbol)
            self.assertIsNotNone(result)
            self.assertIsInstance(result, dict)
            conn.close()
        except Exception as e:
            self.fail(f"Get ETF Overview failed: {e}")

# TestGetETFPerformance aims to test the get_etf_performance function


class TestGetETFPerformance(unittest.TestCase):
    def test_get_etf_performance(self):
        try:
            conn = get_db_connection()
            symbol = "0050"
            result = get_etf_performance(conn, symbol)
            self.assertIsNotNone(result)
            self.assertIsInstance(result, dict)
            conn.close()
        except Exception as e:
            self.fail(f"Get ETF Performance failed: {e}")

# TestGetTopIndustry aims to test the get_top_industry function


class TestGetTopIndustry(unittest.TestCase):
    def test_get_top_industry(self):
        try:
            conn = get_db_connection()
            symbol = "0050"
            result = get_top_industry(conn, symbol)
            self.assertIsNotNone(result)
            self.assertIsInstance(result, list)
            conn.close()
        except Exception as e:
            self.fail(f"Get Top Industry failed: {e}")

# TestGetTop10Stock aims to test the get_top10_stock function


class TestGetTop10Stock(unittest.TestCase):
    def test_get_top10_stock(self):
        try:
            conn = get_db_connection()
            symbol = "0050"
            result = get_top10_stock(conn, symbol)
            self.assertIsNotNone(result)
            self.assertIsInstance(result, list)
            conn.close()
        except Exception as e:
            self.fail(f"Get Top 10 Stock failed: {e}")


if __name__ == '__main__':
    unittest.main()
