import sys
import time
import requests
import argparse
import multiprocessing
# from random import randint
from bs4 import BeautifulSoup
from pymongo import MongoClient
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


def connect_mongo():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['taxcode_db']
    collection = db['taxcodes']
    return collection


def get_data_input():
    parser = argparse.ArgumentParser(description='Crawl tax code with URL')
    parser.add_argument('url', type=str, help='URL parameter')
    args = parser.parse_args()

    return args.url


def get_last_page(url, session):
    response = session.get(url)
    if response.status_code == 200:
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            page_list = soup.find_all('li', class_='page-item')
            last_page = page_list[-2]
            return last_page.a.text
        except Exception as e:
            print(f'[ERROR] An error occurred. Detail: {e}')
            sys.exit()
    else:
        print(f'[ERROR] Request fail. Status code: {response.status_code}. Detail: {response.reason}')
        sys.exit()


def crawl_tax_code(url, session):
    start_time = time.time()
    response = session.get(url)
    end_time = time.time()
    print(f'URL execute time: {end_time - start_time}')
    taxcodes = []
    if response.status_code == 200:
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            taxcodes_element = soup.find_all('i', class_='fa fa-hashtag')

            for taxcode_element in taxcodes_element:
                taxcode = taxcode_element.next_sibling.next_sibling.text
                taxcodes.append(taxcode)
        except Exception as e:
            print(f'[ERROR] An error occurred. Detail: {e}')
            sys.exit()
    else:
        print(f'[ERROR] Request fail. Status code: {response.status_code}. Detail: {response.reason}')
        sys.exit()

    return taxcodes


def process_page(args):
    url_page, session = args
    taxcodes = crawl_tax_code(url_page, session)
    return taxcodes


def create_session():
    session = requests.Session()
    retries = Retry(total=10, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    return session


def main():
    url = get_data_input()
    print(f'[INFO] Start crawling tax code list with {url}')

    session = create_session()
    last_page = int(get_last_page(url, session))
    batch_size = 1000

    all_taxcodes = []
    collection = connect_mongo()
    total_time = 0
    total_insert_success = 0
    with multiprocessing.Pool() as pool:
        for i in range(1, last_page + 1, batch_size):
            start_time = time.time()

            end_page = min(i + batch_size - 1, last_page)
            pages = [(url + f'?page={page}', session) for page in range(i, end_page + 1)]
            results = pool.map(process_page, pages)
            for result in results:
                all_taxcodes.extend(result)
            if all_taxcodes:
                total_insert_success += len(all_taxcodes)
                collection.insert_many([{'taxcode': taxcode} for taxcode in all_taxcodes])
                print(f'[INFO] Inserted {total_insert_success} tax codes to MongoDB')
                all_taxcodes.clear()

            end_time = time.time()
            execution_time = end_time - start_time
            total_time += execution_time
            print(f'[INFO] Execute time: {total_time}')
    print(f'[INFO] Crawl tax code list of {url} successfully')


if __name__ == '__main__':
    main()
