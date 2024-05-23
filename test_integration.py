import unittest
from unittest.mock import patch, MagicMock
from app import app
from models.etf_model import get_top10_stock


class TestETFTop10Stocks(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('utils.get_db_connection')
    @patch('models.etf_model.get_top10_stock')
    def test_get_top10_stock(self, mock_get_top10_stock, mock_get_db_connection):
        # 模拟数据库连接和游标
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # 定义Mock返回值
        mock_top10_stocks = [
            {'symbol': '0050', 'ranking': 1, 'stock_name': 'Stock A',
                'ratio': 15.00, 'data_updated_date': '2024-05-20'},
            {'symbol': '0050', 'ranking': 2, 'stock_name': 'Stock B',
                'ratio': 12.00, 'data_updated_date': '2024-05-20'},
            {'symbol': '0050', 'ranking': 3, 'stock_name': 'Stock C',
                'ratio': 10.00, 'data_updated_date': '2024-05-20'},
            {'symbol': '0050', 'ranking': 4, 'stock_name': 'Stock D',
                'ratio': 9.00, 'data_updated_date': '2024-05-20'},
            {'symbol': '0050', 'ranking': 5, 'stock_name': 'Stock E',
                'ratio': 8.00, 'data_updated_date': '2024-05-20'},
            {'symbol': '0050', 'ranking': 6, 'stock_name': 'Stock F',
                'ratio': 7.00, 'data_updated_date': '2024-05-20'},
            {'symbol': '0050', 'ranking': 7, 'stock_name': 'Stock G',
                'ratio': 6.00, 'data_updated_date': '2024-05-20'},
            {'symbol': '0050', 'ranking': 8, 'stock_name': 'Stock H',
                'ratio': 5.00, 'data_updated_date': '2024-05-20'},
            {'symbol': '0050', 'ranking': 9, 'stock_name': 'Stock I',
                'ratio': 4.00, 'data_updated_date': '2024-05-20'},
            {'symbol': '0050', 'ranking': 10, 'stock_name': 'Stock J',
                'ratio': 3.00, 'data_updated_date': '2024-05-20'}
        ]

        # 计算 '其他' 占比
        total_ratio = sum(stock['ratio'] for stock in mock_top10_stocks)
        other_ratio = max(100 - total_ratio, 0)
        mock_top10_stocks.append({'symbol': '0050', 'ranking': '其他', 'stock_name': '其他', 'ratio': f"{
                                 other_ratio:.2f}%", 'data_updated_date': '2024-05-20'})

        mock_cursor.fetchall.return_value = mock_top10_stocks
        mock_cursor.fetchone.return_value = {'total_ratio': total_ratio}

        # 模拟执行 SQL 查询
        mock_cursor.execute.return_value = None

        mock_get_top10_stock.return_value = mock_top10_stocks

        # 发出 GET 请求到相应的 Route
        response = self.app.get('/search-results?symbol=0050')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()

        # 确认返回的结果是否符合预期
        self.assertIsInstance(data, dict)
        top10_stocks = data['etfStockData']['etf1']

        self.assertEqual(len(top10_stocks), 11)  # 包括前十大成分股和其他占比

        for i in range(10):
            self.assertEqual(
                top10_stocks[i]['stock_name'], f'Stock {chr(65 + i)}')
            self.assertEqual(top10_stocks[i]['ratio'], f"""{
                             mock_top10_stocks[i]['ratio']:.2f}%""")

        self.assertEqual(top10_stocks[10]['stock_name'], '其他')
        self.assertEqual(top10_stocks[10]['ratio'], f"{other_ratio:.2f}%")


if __name__ == '__main__':
    unittest.main()
