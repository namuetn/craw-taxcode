import base64
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from pathlib import Path
import cv2

def crawl_captcha_v2():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    for i in range(50):
        driver.get("https://tracuunnt.gdt.gov.vn/tcnnt/mstdn.jsp")
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        captcha_screenshot = driver.find_element(by=By.XPATH, value="//*[@id='tcmst']/form/table/tbody/tr[6]/td[2]/table/tbody/tr/td[2]")
        check_exists_folder('./screenshots')
        captcha_path = f"./screenshots/captcha-{i}.png"
        captcha_screenshot.screenshot(captcha_path)
        # preprocess_captcha_image(captcha_path)


def check_exists_folder(path):
    p = Path(path)
    if not p.is_dir():
        p.mkdir(parents=True, exist_ok=True)


def preprocess_captcha_image(path):
    image = cv2.imread(path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Áp dụng GaussianBlur để làm mờ ảnh
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                cv2.THRESH_BINARY, 155, 122)
    cv2.imwrite(path, binary)

if __name__ == "__main__":
    crawl_captcha_v2()