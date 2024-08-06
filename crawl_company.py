import cv2
import time
import asyncio
import ddddocr
import requests
import numpy as np
from PIL import Image
from io import BytesIO
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from pymongo import MongoClient
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService

def connection_database():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['taxcode_db']
    collection = db['taxcodes']

    return collection


def extract_image_to_text(image_data, ocr):
    # image = open(path, "rb").read()
    text = ocr.classification(image_data, png_fix=True)

    return text if text != "" else "no"



def check_exists_folder(path):
    p = Path(path)
    if not p.is_dir():
        p.mkdir(parents=True, exist_ok=True)


def wait_until_page_finishes_loading(driver):
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )


def check_error_message(driver, tag):
    try:
        result = driver.find_element(by=By.XPATH, value=f"//*[@id='tcmst']/{tag}").text
        return result
    except NoSuchElementException:
        return ''


def fill_captcha(driver, ocr):
    captcha_input = driver.find_element(by=By.ID, value="captcha")
    captcha_screenshot = driver.find_element(by=By.XPATH, value="//*[@id='tcmst']/form/table/tbody/tr[6]/td[2]/table/tbody/tr/td[2]")

    # Chụp ảnh captcha vào bộ nhớ
    captcha_image = captcha_screenshot.screenshot_as_png
    image = Image.open(BytesIO(captcha_image))

    # Chuyển đổi ảnh sang định dạng OpenCV
    opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Tiền xử lý ảnh trực tiếp
    processed_image = preprocess_captcha_image(opencv_image)

    processed_image_data = cv2.imencode('.png', processed_image)[1].tobytes()
    captcha_text = extract_image_to_text(processed_image_data, ocr)
    captcha_input.send_keys(captcha_text)

    submit_button = driver.find_element(by=By.CLASS_NAME, value="subBtn")
    submit_button.click()

    return captcha_text


def preprocess_captcha_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Áp dụng GaussianBlur để làm mờ ảnh
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 155, 122)

    return binary


def convert_business_line_to_string(business_list):
    business_names = [item['business_name'] for item in business_list]
    result_string = ' '.join(business_names)

    return result_string


def convert_status_field(note):
    active_status = ['đang hoạt động', 'tạm ngừng hoạt động']
    inactive_status = ['ngừng hoạt động', 'không hoạt động']
    for status in active_status:
        if status in note:
            return 'active'
    for status in inactive_status:
        if status in note:
            return 'inactive'
    return 'unknown'



def crawl_overall_company(row):
    cells = row.find_elements(by=By.TAG_NAME, value="td")
    taxcode = cells[1].text
    company = {
        "tax_identification_number": cells[1].text,
        "status": convert_status_field(cells[6].text),
        "raw_data": {
            "tax_identification_number": cells[1].text,
            "taxpayer": cells[2].text,
            "tax_authority": cells[3].text,
            "id_card": cells[4].text,
            "recent_change_time": cells[5].text,
            "note": cells[6].text,
        }
    }

    return taxcode, company

async def crawl_detail_company(driver, company, taxcode):
    driver.execute_script(f"javascript:submitform('{taxcode}')")
    wait_until_page_finishes_loading(driver)
    
    extra_data = driver.find_elements(by=By.XPATH, value="//*[@id='AutoNumber2']/tbody/tr/td/input")
    
    # Tạo danh sách các coroutine
    tasks = [
        crawl_managing_enterprise(driver, extra_data[0], company, taxcode),
        crawl_member_unit(driver, extra_data[1], company, taxcode),
        crawl_subordinate_unit(driver, extra_data[2], company, taxcode),
        crawl_representative_office(driver, extra_data[3], company, taxcode),
        crawl_type_tax_payable(driver, extra_data[4], company, taxcode),
        crawl_business_line(driver, extra_data[5], company, taxcode)
    ]

    await asyncio.gather(*tasks)

    business_line = convert_business_line_to_string(company['raw_data']['business_line'])

    cells = driver.find_elements(by=By.XPATH, value="//*[@id='tcmst']/table/tbody/tr/td")
    company.update(
        {
            "name": cells[3].text,
            "legal_representative": cells[21].text,
            "address": cells[6].text,
            "license_time": cells[1].text,
            "active_time": cells[17].text,
            "phone_number": '',
            "email": '',
            "business_type": '',
            "website": '',
            "chartered_capital": '',
            "abbreviated_name": cells[4].text,
            "foreign_name": cells[4].text,
            "business_sector": business_line,
        }
    )
    company['raw_data'].update(
        {
            "taxcode_open_time": cells[1].text,
            "taxcode_close_time": cells[2].text,
            "original_company_name": cells[3].text,
            "trading_name": cells[4].text,
            "place_of_tax_administration": cells[5].text,
            "address": cells[6].text,
            "place_of_tax_payment": cells[7].text,
            "address_receive_tax_notices": cells[8].text,
            "QDTL_time": cells[9].text,
            "decision_making_agency": cells[10].text,
            "GPKD_time": cells[11].text,
            "providing_agency": cells[12].text,
            "receipt_declaration_time": cells[13].text,
            "day_month_financial_year_started_time": cells[14].text,
            "day_month_financial_year_ended_time": cells[15].text,
            "current_code": cells[16].text,
            "commencement_operations_time": cells[17].text,
            "chapter_clause": cells[18].text,
            "accounting_form": cells[19].text,
            "vat_method": cells[20].text,
            "legal_representative": cells[21].text,
            "legal_representative_address": cells[22].text,
            "direction_name": cells[23].text,
            "direction_address": cells[24].text,
            "chief_accountant_name": cells[25].text,
            "chief_accountant_address": cells[26].text,
        }
    )

    return company


def create_headers(driver):
    cookies = driver.get_cookies()
    cookie_header = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'Cookie': cookie_header,
        'Accept': '*/*'
    }

    return headers


async def crawl_managing_enterprise(driver, button, company, taxcode):
    button.click()
    headers = create_headers(driver)
    data = {
        'tin': taxcode
    }

    response = requests.post('https://tracuunnt.gdt.gov.vn/tcnnt/doanhnghiepchuquan.jsp', headers=headers, data=data, verify=False)
    soup = BeautifulSoup(response.text, 'lxml')
    rows = soup.find_all('tr')
    if len(rows) <= 1:
        company['raw_data'].update({
            "managing_enterprise": []
        })

    data = []
    for row in rows[1:len(rows)]:
        cells = row.find_all('td')
        data.append({
            "taxcode": cells[1].text.strip(),
            "managing_enterprise": cells[2].text.strip(),
            "address": cells[3].text.strip(),
            "vat_method": cells[4].text.strip(),
        })
    
    company['raw_data'].update({
        "managing_enterprise": data
    })


async def crawl_member_unit(driver, button, company, taxcode):
    button.click()
    headers = create_headers(driver)
    data = {
        'tin': taxcode
    }

    response = requests.post('https://tracuunnt.gdt.gov.vn/tcnnt/chinhanh.jsp', headers=headers, data=data, verify=False)
    soup = BeautifulSoup(response.text, 'lxml')
    rows = soup.find_all('tr')
    if len(rows) <= 1:
        company['raw_data'].update({
            "member_unit": []
        })

    data = []
    for row in rows[1:len(rows)]:
        cells = row.find_all('td')
        data.append({
            "taxcode": cells[1].text.strip(),
            "member_name": cells[2].text.strip(),
            "address": cells[3].text.strip(),
            "province_code": cells[4].text.strip(),
            "district_code": cells[5].text.strip(),
            "province_name": cells[6].text.strip(),
            "district_name": cells[7].text.strip(),
        })
    
    company['raw_data'].update({
        "member_unit": data
    })
    # button.click()
    # time.sleep(0.05)
    # rows = driver.find_elements(by=By.XPATH, value="//*[@id='wap_content']/table/tbody/tr")
    # if len(rows) <= 1:
    #     company['raw_data'].update({
    #         "member_unit": []
    #     })

    # data = []
    # for row in rows[1:len(rows)]:
    #     cells = row.find_elements(by=By.TAG_NAME, value="td")
    #     data.append({
    #         "taxcode": cells[1].text,
    #         "member_name": cells[2].text,
    #         "address": cells[3].text,
    #         "province_code": cells[4].text,
    #         "district_code": cells[5].text,
    #         "province_name": cells[6].text,
    #         "district_name": cells[7].text,
    #     })

    # company['raw_data'].update({
    #     "member_unit": data
    # })


async def crawl_subordinate_unit(driver, button, company, taxcode):
    button.click()
    headers = create_headers(driver)
    data = {
        'tin': taxcode
    }

    response = requests.post('https://tracuunnt.gdt.gov.vn/tcnnt/tructhuoc.jsp', headers=headers, data=data, verify=False)
    soup = BeautifulSoup(response.text, 'lxml')
    rows = soup.find_all('tr')
    if len(rows) <= 1:
        company['raw_data'].update({
            "subordinate_unit": []
        })

    data = []
    for row in rows[1:len(rows)]:
        cells = row.find_all('td')
        data.append({
            "taxcode": cells[1].text.strip(),
            "unit_name": cells[2].text.strip(),
            "address": cells[3].text.strip(),
            "province_code": cells[4].text.strip(),
            "district_code": cells[5].text.strip(),
            "province_name": cells[6].text.strip(),
            "district_name": cells[7].text.strip(),
        })

    company['raw_data'].update({
        "subordinate_unit": data
    })


async def crawl_representative_office(driver, button, company, taxcode):
    button.click()
    headers = create_headers(driver)
    data = {
        'tin': taxcode
    }

    response = requests.post('https://tracuunnt.gdt.gov.vn/tcnnt/daidien.jsp', headers=headers, data=data, verify=False)
    soup = BeautifulSoup(response.text, 'lxml')
    rows = soup.find_all('tr')
    if len(rows) <= 1:
        company['raw_data'].update({
            "representative_office": []
        })

    data = []
    for row in rows[1:len(rows)]:
        cells = row.find_all('td')
        data.append({
            "taxcode": cells[1].text.strip(),
            "member_name": cells[2].text.strip(),
            "address": cells[3].text.strip(),
            "province_code": cells[4].text.strip(),
            "district_code": cells[5].text.strip(),
            "province_name": cells[6].text.strip(),
            "district_name": cells[7].text.strip(),
        })
    
    company['raw_data'].update({
        "representative_office": data
    })


async def crawl_type_tax_payable(driver, button, company, taxcode):
    button.click()
    headers = create_headers(driver)
    data = {
        'tin': taxcode
    }

    response = requests.post('https://tracuunnt.gdt.gov.vn/tcnnt/loaithue.jsp', headers=headers, data=data, verify=False)
    soup = BeautifulSoup(response.text, 'lxml')
    rows = soup.find_all('tr')
    if len(rows) <= 1:
        company['raw_data'].update({
            "type_tax_payable": []
        })

    data = []
    for row in rows[1:len(rows)]:
        cells = row.find_all('td')
        data.append({
            "type_of_taxcode": cells[1].text.strip(),
            "name": cells[2].text.strip(),
        })
    
    company['raw_data'].update({
        "type_tax_payable": data
    })


async def crawl_business_line(driver, button, company, taxcode):
    button.click()
    headers = create_headers(driver)
    data = {
        'tin': taxcode
    }

    response = requests.post('https://tracuunnt.gdt.gov.vn/tcnnt/nganhkinhdoanh.jsp', headers=headers, data=data, verify=False)
    soup = BeautifulSoup(response.text, 'lxml')
    rows = soup.find_all('tr')
    if len(rows) <= 1:
        company['raw_data'].update({
            "business_line": []
        })

    data = []
    for row in rows[1:len(rows)]:
        cells = row.find_all('td')
        data.append({
            "business_code": cells[1].text,
            "business_name": cells[2].text,
            "is_main_business": True if cells[3].text == 'Y' else False,
        })
    
    company['raw_data'].update({
        "business_line": data
    })


async def crawl_all_company():
    # define ocr captcha images
    ocr = ddddocr.DdddOcr()

    # try:
    start_time = time.time()

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    # driver = webdriver.Chrome()

    driver.get("https://tracuunnt.gdt.gov.vn/tcnnt/mstdn.jsp")
    end_time1 = time.time()
    print(f"[INFO] Executime of selenium: {end_time1-start_time}")
    count_retry = 0
    max_retry = 10
    while True:
        wait_until_page_finishes_loading(driver)

        taxcodes_input = driver.find_element(by=By.NAME, value="mst")
        taxcodes_input.send_keys('0107899950')

        captcha_text = fill_captcha(driver, ocr)

        wait_until_page_finishes_loading(driver)
        driver.find_element(by=By.NAME, value="mst").clear()

        # check bypass captcha suceess or fail
        if check_error_message(driver, "div") == "Bạn chưa nhập đủ các thông tin cần thiết.":
            print("[ERROR] Haven't entered all the necessary information")
            break

        if check_error_message(driver, "p") == "Vui lòng nhập đúng mã xác nhận!":
            print("[ERROR] Captcha is wrong")
            count_retry += 1
            if count_retry == max_retry:
                print('[ERROR] Maximum retry reached')
                break
            continue

        rows = driver.find_elements(by=By.XPATH, value="//*[@id='tcmst']/table/tbody/tr")
        if len(rows) <= 2: # no data found
            row = rows[1]
            cell_name = row.find_element(by=By.TAG_NAME, value="td").text
            if cell_name == "Không tìm thấy người nộp thuế nào phù hợp.":
                print('[INFO] No data found')
                break

        taxcode, company = crawl_overall_company(rows[1]) # rows[1] bởi vì chỉ crawl chính xác MST đó thôi, MST con thì sẽ được crawl khi fill vào input
        company = crawl_detail_company(driver, company, taxcode)

        break
    end_time = time.time()
    print(f'[INFO] Execute time all: {end_time - start_time}')
    abc=123
    # except Exception as e:
    #     print(f'[ERROR] {e}')
    #     driver.quit

    driver.quit


if __name__ == '__main__':
    screenshot_folder = 'screenshot'
    print('[INFO] Start crawl tax code...')
    asyncio.run(crawl_all_company())
