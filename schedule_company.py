import time
import ddddocr
import asyncio
import multiprocessing
from multiprocessing import Process, current_process
from pymongo import MongoClient
from crawl_company import crawl_all_company
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

def connection_database():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['taxcode_db']
    return db

async def process_taxcodes(taxcodes, ocr, chrome_options):
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    driver.get("https://tracuunnt.gdt.gov.vn/tcnnt/mstdn.jsp")
    companies = []
    
    for taxcode in taxcodes:
        companies.append(await crawl_all_company(ocr, driver, chrome_options, taxcode))
    
    driver.quit()
    return companies

def worker(taxcodes):
    print(f'taxcode: {taxcodes} and process: {current_process().name}')
    ocr = ddddocr.DdddOcr()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(process_taxcodes(taxcodes, ocr, chrome_options))
    return result

def main():
    taxcodes_queue_db = connection_database()
    taxcodes_queue = taxcodes_queue_db['taxcodes_queue'].find_one()
    taxcodes = taxcodes_queue['taxcodes'][0:16]

    num_processes = 5
    chunk_size = len(taxcodes) // num_processes

    # Divide the taxcodes into chunks
    chunks = [taxcodes[i:i + chunk_size] for i in range(0, len(taxcodes), chunk_size)]

    start_time = time.time()

    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(worker, chunks)

    # Flatten the list of results
    companies = [company for sublist in results for company in sublist]

    end_time = time.time()
    print(f"[INFO] Final execute time: {end_time-start_time}")

if __name__ == '__main__':
    main()