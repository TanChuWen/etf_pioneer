import requests
from bs4 import BeautifulSoup
import json
import os
import boto3
from dotenv import load_dotenv
import datetime
import time
import re

# Load environment variables from .env file
load_dotenv()

#####
s3 = boto3.client('s3',
                  aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                  aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                  region_name=os.getenv("S3_BUCKET_REGION"))
BUCKET_NAME = os.getenv("BUCKET_NAME")
#####
stock_list = []
today = datetime.datetime.now().strftime("%Y/%m/%d")
today_file = datetime.datetime.now().strftime("%Y-%m-%d")


def save_data_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data has been written to {filename}")


def upload_file_to_s3(filename, BUCKET_NAME):
    """Uploads a file to an S3 bucket."""
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(filename, BUCKET_NAME, filename)
        print(f"Successfully uploaded {filename} to S3 bucket {BUCKET_NAME}")
    except Exception as e:
        print(f"Failed to upload {filename}. Error: {str(e)}")


##### Fetch stock list from TWSE website #####
url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'h4'})
    rows = table.find_all('tr')[1:]  # skip the header row
    # Get the data updated time
    center_tags = soup.find_all('center')
    date_str = None
    for tag in center_tags:
        if re.search(r'\d{4}/\d{2}/\d{2}', tag.text):
            date_str = re.search(r'\d{4}/\d{2}/\d{2}', tag.text).group()
            break

    if date_str:
        data_updated_time = date_str
    else:
        data_updated_time = "NULL"

    for row in rows:
        cells = row.find_all('td')
        if len(cells) > 4:
            code_and_name = cells[0].text.strip().split()
            # code and name are separated by a space
            if len(code_and_name) >= 2:
                stock_code = code_and_name[0]
                stock_name = " ".join(code_and_name[1:])
                listed_or_OTC = cells[3].text.strip()
                industry_category = cells[4].text.strip()

                stock_list.append({
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "listed_or_OTC": listed_or_OTC,
                    "industry_category": industry_category,
                    "data_updated_date": data_updated_time,
                    "crawler_date": today
                })
else:
    print("Failed to fetch data from TWSE website.")


# Save data to a JSON file
filename = f"stock_list_{today_file}.json"
save_data_to_json(stock_list, filename)
upload_file_to_s3(filename, BUCKET_NAME)
