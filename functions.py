from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait, Select 
from selenium.webdriver.support import expected_conditions as EC  
from selenium.common.exceptions import NoSuchElementException
import time

url = 'https://yc.gxnu.edu.cn/'

def logout():
    driver = webdriver.Edge()
    driver.get(url)
    driver.maximize_window()

    time.sleep(1) 

    logout_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "logout"))  
    )
    logout_btn.click()

    time.sleep(1)

    confirm_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "layui-layer-btn0"))
    )
    confirm_btn.click()

    time.sleep(3) 

    driver.quit()

def login(username, password, way, pre_refresh=False):
    '''
    way: 
    '0' for campus network, 
    '1' for China Telecom, 
    '2' for China Unicom, 
    '3' for China Mobile
    '''
    driver = webdriver.Edge()
    driver.get(url)
    driver.maximize_window()

    if pre_refresh:
        time.sleep(5)
        driver.refresh()

    time.sleep(1)  

    reset_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@value='重置']")) 
    )
    reset_btn.click()

    time.sleep(1)

    username_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='账号']"))
    )
    username_input.send_keys(username)

    time.sleep(1)

    password_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='密码']"))
    )
    password_input.send_keys(password)

    time.sleep(1)
    
    isp_select = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "ISP_select"))
    )
    select = Select(isp_select)
    way_str = str(way)
    try:
        select.select_by_value(way_str)
    except NoSuchElementException:
        wifi_map = {'0': '', '1': '@ctc', '2': '@cuc', '3': '@cmc'}
        select.select_by_value(wifi_map.get(way_str, ''))
    
    time.sleep(1)

    login_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@value='登录']"))
    )
    login_btn.click()

    time.sleep(3) 

    driver.quit()

if __name__ == "__main__":
    logout()
    username = 'xxxxxxxxxx'
    password = 'xxxxxx'

    login(username, password, way=1)
