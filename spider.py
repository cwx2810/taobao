import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)

#模拟搜索
def search():
    try:
        browser.get('http://www.taobao.com')
        #等待搜索框加载
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#q')))
        #等待查询按钮加载
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
        #模拟输入、点击
        input.send_keys('美食')
        submit.click()
        #等待总页码加载
        total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
        return total.text
    except TimeoutException:
        return search()

def main():
    total = search()
    #在共100页中匹配出100数字
    total = int(re.compile('(\d+)').search(total).group(1))
    print(total)

if __name__ == '__main__':
    main()