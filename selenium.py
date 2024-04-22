from selenium import webdriver # type: ignore
from selenium.webdriver.chrome.service import Service # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.common.keys import Keys # type: ignore
import requests # type: ignore
from bs4 import BeautifulSoup
import time
import re
import json

class Reporter:
    def fetch(self, driver, query):
        url = f'https://search.naver.com/search.naver?where=news&query={query}'
        driver.get(url)
        
        body = driver.find_element(By.TAG_NAME, 'body')
        
        for _ in range(10):
            body.send_keys(Keys.END)
            time.sleep(1)

        news_links = driver.find_elements(By.CSS_SELECTOR, 'div.news_wrap > div.news_area > div.news_contents > a.news_tit')
        results = []
        for link in news_links:
            href = link.get_attribute('href')
            results.append({'title': link.text, 'href': href})

        return results
    
    @staticmethod
    def findEmails(url):
        response = requests.get(url)
        
        soup = BeautifulSoup(response.text, 'html.parser')

        emails = set()
        for string in soup.find_all(string=re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')):
            emails.update(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', string))
        
        return list(emails)

if __name__ == '__main__':
    query = '대학 스타트업'
    news_list = []

    service = Service('./chromedriver')
    driver = webdriver.Chrome(service=service)
    reporter = Reporter()
    
    try:
        news_list = reporter.fetch(driver=driver, query=query)
    finally:
        driver.quit()

    for news in news_list:
        try:
            news['emails'] = Reporter.findEmails(news['href'])
            print(news)
        except:
            news['emails'] = 'error'
            print(news)
    
    with open(f'{query}.txt', 'w', encoding='utf8') as file:
        json.dump(news_list, file, ensure_ascii=False)