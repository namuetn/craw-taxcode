import os
import sys
import json
import requests
import argparse
from bs4 import BeautifulSoup
import multiprocessing


def append_to_json_file(file_save, data):
    try:
        with open(file_save, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = []

    existing_data.extend(data)

    with open(file_save, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)


def get_data_input():
    parser = argparse.ArgumentParser(description='Crawl tax code with URL')
    parser.add_argument('url', type=str, help='URL parameter')
    args = parser.parse_args()

    return args.url


def get_last_page(url):
    response = requests.get(url)
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


def crawl_tax_code(url):
    response = requests.get(url)

    taxcodes = []
    total_taxcode = 0
    if response.status_code == 200:
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            taxcodes_element = soup.find_all('i', class_='fa fa-hashtag')

            for taxcode_element in taxcodes_element:
                taxcode = taxcode_element.next_sibling.next_sibling.text
                taxcodes.append(taxcode)
                total_taxcode += 1
        except Exception as e:
            print(f'[ERROR] An error occurred. Detail: {e}')
            sys.exit()

        append_to_json_file('./dist/taxcodes.json', taxcodes)
        return total_taxcode
    else:
        print(f'[ERROR] Request fail. Status code: {response.status_code}. Detail: {response.reason}')
        sys.exit()


def process_page(page):
    url_page = url + f'?page={page}'
    total_taxcode = crawl_tax_code(url_page)
    print(f'[INFO] Total of Page {page}: {total_taxcode}')
    return total_taxcode


if __name__ == '__main__':
    city_filename = './dist/cities.json'
    taxcode_filename = './dist/taxcodes.json'
    
    try:
        os.remove(taxcode_filename)
    except OSError:
        pass
    
    url = get_data_input()
    print(f'[INFO] Start crawling text code list ...')
    last_page = int(get_last_page(url))

    final_total = 0
    # for page in range(1, last_page):
    #     url_page = url + f'?page={page}'

    #     total_taxcode = crawl_tax_code(url_page, taxcode_filename)
    #     final_total += total_taxcode
    #     print(f'[INFO] Total of Page {page}: {final_total}')
    with multiprocessing.Pool() as pool:
        results = pool.map(process_page, range(1, 1001))
        final_total = sum(results)

    print(f'[INFO] Crawl tax code list successfully. Save at {taxcode_filename}')    
