import base64
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time


driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.get("https://tracuunnt.gdt.gov.vn/tcnnt/mstdn.jsp")

# canvas = driver.find_elements(by=By.XPATH, value="//*[@id="tcmst"]/form/table/tbody/tr[6]/td[2]/table/tbody/tr/td[2]/div/img")
# get the canvas as a PNG base64 string
for i in range(1000):
    script_js = '''
        const imgElement = document.querySelector("#tcmst > form > table > tbody > tr:nth-child(6) > td:nth-child(2) > table > tbody > tr > td:nth-child(2) > div > img");
        const imgSrc = imgElement.src;
        const link = document.createElement('a');
        link.href = imgSrc;
        link.download = 'captcha111111.png';
        document.body.appendChild(link);
        link.click();
    '''
    driver.execute_script(script_js)
    time.sleep(1)
