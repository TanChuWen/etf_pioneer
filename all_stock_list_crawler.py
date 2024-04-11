import requests
from bs4 import BeautifulSoup

url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table', {'class': 'h4'})
    rows = table.find_all('tr')[1:]  # skip the header row

    for row in rows:
        data = row.find_all('td')
        if len(data) > 0:
            code_and_name = data[0].text.strip().split()
            # code and name are separated by a space
            if len(code_and_name) >= 2:
                stock_code = code_and_name[0]
                stock_name = code_and_name[1]
            else:
                print("Failed to parse stock code and name.")
                continue

            market_category = data[3].text.strip()
            industry_category = data[4].text.strip()

            print(stock_code, stock_name, market_category, industry_category)


else:
    print("Failed to fetch data from TWSE website.")
