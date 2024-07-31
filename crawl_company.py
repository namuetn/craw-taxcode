from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def get_captcha_images():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    print('[INFO] Start crawl tax code...')
    count = 0
    while True:
        try:
            taxcodes_element = driver.find_elements(by=By.XPATH, value="/html/body/main/div/div[@class='col-md-8']/div[@class='card mb-2']/div[@class='card-body']/p[@class='card-title']/a")
            taxcodes_data = []
            for city in taxcodes_element:
                taxcodes_data.append(city.text)
            print(taxcodes_data)

            next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/main/div/div[@class='col-md-8']/div[@class='mt-3']/nav/ul/li/a[text()='›']")))
            driver.execute_script("arguments[0].scrollIntoView();", next_button)
            driver.execute_script("arguments[0].click();", next_button)

            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            # export_json(filename, taxcodes_data)

            count += len(taxcodes_data)
            print(f"Đã save {count}/282067 data vào json")
        except Exception as e:
            print(f'[ERROR] {e}')
            driver.quit

            break


    print(f'[INFO] Total: {count} text_code')

    driver.quit