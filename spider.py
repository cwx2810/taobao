import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
from config import *
import pymongo

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

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
        get_prodects()
        return total.text
    except TimeoutException:
        return search()

# 模拟点击下一页
def next_page(page_number):
    try:
        # 等待页码输入框加载
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
        # 等待确定按钮加载
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        # 清楚页码输入框数字
        input.clear()
        # 输入页码
        input.send_keys(page_number)
        #点击确认
        submit.click()
        # 等待页码高亮元素显示我们想转到的那一页
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_number)))
        get_prodects()
    except TimeoutException:
        next_page(page_number)

# 获取网页信息
def get_prodects():
    # 判断商品是否加载成功
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
    # 拿到网页源代码
    html = browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('src'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text()[:-3],
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()
        }
        print(product)
        save_to_mongo(product)

# 保存到数据库
def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('保存到mongoDB成功!', result)
    except Exception:
        print('保存到mongoDB错误!', result)

def main():
    total = search()
    #在共100页中匹配出100数字
    total = int(re.compile('(\d+)').search(total).group(1))
    # 遍历翻100页
    for i in range(2, total + 1):
        next_page(i)

if __name__ == '__main__':
    main()