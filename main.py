import datetime
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException


json_path = 'json.json'
parsed_links_path = 'parsed_links.txt'
all_news_list = []

dictionary = {
    'https://www.datacenterdynamics.com/en/news/': {
        'a_xpath': "//a[@class='block-link headline-link']",
        'title': "//h1[@class='article-heading']",
        'body': "//div[@class='block-text']",
        'teaser': "//div[@class='article-sub-heading']/p",
        'short_name': "datacenterdynamics"
    },
    'https://www.datacenterfrontier.com/': {
        'a_xpath': "//a[@class='title-wrapper']",
        'title': "//h1[@class='title-text']",
        'body': "//p",
        'teaser': "//div[@class='teaser-text']",
        'short_name': "datacenterfrontier"
    },
    'https://www.datacenterknowledge.com/': {
        'a_xpath': "//div[@class='title']/a",
        'title': "//h1[@itemprop='headline']",
        'body': "//div[@itemprop='articleBody']",
        'teaser': "//div[@class='field field-name-field-penton-content-summary field-type-text-long field-label-hidden']",
        'short_name': "datacenterknowledge"
    },
    'https://datacentre.solutions/news': {
        'a_xpath': "//h5[a[@class='text-dark']]/a",
        'title': "//div[@class='postSection']/h1",
        'body': "//div[@class='post-details']//p",
        'teaser': "//div[@class='postSection']/h2",
        'short_name': "datacentre.solutions"
    },
    'https://datacentrereview.com/': {
        'a_xpath': "//h5[@class='sc_blogger_item_title entry-title']/a",
        'title': "//h1",
        'body': "//div[@class='elementor-widget-container']/p",
        'teaser': None,
        'short_name': "datacentrereview"
    },
    'https://dcnnmagazine.com/': {
        'a_xpath': "//h3[@class='jeg_post_title']/a",
        'title': "//h1",
        'body': "//div[@class='content-inner  jeg_link_underline']//p",
        'teaser': None,
        'short_name': "dcnnmagazine"
    },
    'https://datacenternews.asia/': {
        'a_xpath': "//a[@class='flex flex-col md:flex-row gap-4 hover:opacity-75']",
        'title': "//h1",
        'body': "//div[@class='flex flex-col lg:flex-row gap-x-10 gap-y-5']/div[2]",
        'teaser': None,
        'short_name': "datacenternews"
    },
    'https://www.capacitymedia.com/news': {
        'a_xpath': "//div[@class='PromoB-title']/a",
        'title': "//h1",
        'body': "//div[@class='RichTextArticleBody-body RichTextBody']/p",
        'teaser': "//h2[@class='ArticlePage-subHeadline']",
        'short_name': "capacitymedia"
    }
}

with open(parsed_links_path, 'a+') as f:
    f.seek(0)
    parsed_links = set(line.strip() for line in f)

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)
for link, details in dictionary.items():
    driver.get(link)
    time.sleep(1)
    a_xpath = details['a_xpath']
    news_links = driver.find_elements(By.XPATH, a_xpath)
    for li in news_links:
        news_link = li.get_attribute('href')
        if news_link not in parsed_links and 'datacenterfrontier.com/careers/' not in news_links:
            all_news_list.append(news_link)

driver.close()
print(all_news_list)

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)
date_today = datetime.datetime.today().strftime('%d.%m.%Y')
for link in all_news_list:
    try:
        driver.get(link)
        time.sleep(0.2)
        title = teaser = body = ''
        for _, details in dictionary.items():
            if details['short_name'] in link:
                try:
                    title = driver.find_element(By.XPATH, details['title']).text
                    if teaser:
                        teaser = driver.find_element(By.XPATH, details['teaser']).text
                    else:
                        teaser = None
                    body_elements = driver.find_elements(By.XPATH, details['body'])
                    for text in body_elements:
                        body += text.text.replace('\n', ' ')
                    break
                except NoSuchElementException:
                    print(link, 'ERROR!')

        article_data = {
            "date": date_today,
            "link": link,
            "title": title,
            "teaser": teaser,
            "body": body
        }

        with open(json_path, 'a') as json_file:
            json.dump(article_data, json_file)
            json_file.write('\n')

        with open(parsed_links_path, 'a') as f:
            f.write(link + '\n')
    except TimeoutException:
        # If the page or the elements don't load within 10 seconds, skip to the next link
        print(f"Timeout for {link}, moving to the next link.")
        continue

driver.close()