import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from fake_useragent import UserAgent
from lxml import etree
import re


class Book:
    def __init__(self):
        self.etree = etree
        self.requests=requests.Session()
        self.headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0'
        }

    def get_page(self):
        url='https://www.wenku8.net/'
        ua = UserAgent()
        user_agent = ua.random
        options = webdriver.EdgeOptions()
        # options.add_argument('--headless')  # 使用无头模式运行浏览器，不打开实际窗口
        options.add_argument(f'user-agent={user_agent}')
        driver = webdriver.Edge(options=options)
        driver.get(url)

        # 等待元素加载完成
        wait = WebDriverWait(driver, 10)
        driver.find_element(By.XPATH,"/html/body/div[4]/div/div/form/table/tbody/tr[1]/td/table/tbody/tr[1]/td[2]/input").send_keys("18377398197@163.com")
        time.sleep(6)
        driver.find_element(By.XPATH,"/html/body/div[4]/div/div/form/table/tbody/tr[1]/td/table/tbody/tr[2]/td[2]/input").send_keys("fjchg556")
        time.sleep(2)
        driver.find_element(By.XPATH,"/html/body/div[4]/div/div/form/table/tbody/tr[1]/td/table/tbody/tr[4]/td[2]/input").click()
        time.sleep(8)
        driver.find_element(By.XPATH,"/html/body/div[6]/div[1]/div[3]/div[2]/div/a").click()
        time.sleep(8)
        page=driver.page_source
        driver.find_element(By.XPATH,"/html/body/div[5]/div[2]/div/form/table/tbody/tr[2]/td[2]/a")
        driver.quit()
        return page

    def get_book(self):
        page=self.get_page()
        page=etree.HTML(page)
        book_num=page.xpath('/html/body/div[5]/div[2]/div/form/table/tbody')
        book_num=len(book_num[0].xpath('.//tr'))
        #/html/body/div[5]/div[2]/div/form/table/tbody/tr[2]
        #/html/body/div[5]/div[2]/div/form/table/tbody/tr[1]
        book_names=[]
        book_urls=[]
        book_ids =[]
        book_artists =[]
        book_covers =[]
        for i in range(2,book_num):
            book_name=page.xpath(f'/html/body/div[5]/div[2]/div/form/table/tbody/tr[{i}]/td[2]/a')[0]
            # url
            book_url=book_name.get('href')
            book_urls.append(book_url)
            # 名字
            book_name = book_name.text.strip()
            book_names.append(book_name)
            # id
            book_id=book_url.split("=")[1]
            book_id=book_id[:4]
            book_id=re.sub(r'[^0-9]', '', book_id)
            book_ids.append(book_id)
            # 作者
            book_artist=page.xpath(f'/html/body/div[5]/div[2]/div/form/table/tbody/tr[{i}]/td[3]/a')[0]
            book_artist=book_artist.text.strip()
            book_artists.append(book_artist)
            # 封面
            for j in range(0,10):
                time.sleep(0.5)
                if self.requests.get(f'http://img.wenku8.com/image/{str(j)}/{book_id}/{book_id}s.jpg',headers=self.headers).status_code != 404:
                    book_cover=f'http://img.wenku8.com/image/{str(j)}/{book_id}/{book_id}s.jpg'
                    book_covers.append(book_cover)
                    break
        self.requests.close()
        return {
            'title':book_names,#列表
            'book_url':book_urls,#列表
            'book_id':book_ids,#列表
            'author':book_artists,#列表
            'cover_image':book_covers#列表
        }