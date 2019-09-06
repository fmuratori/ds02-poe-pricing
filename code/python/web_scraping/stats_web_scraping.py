import threading
import time
from datetime import datetime

import logging

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# BROWSER_DRIVE = '/home/fabio/Desktop/ds02-poe-pricing/data/geckodriver'

URL_POE_NINJA = 'https://poe.ninja/stats'
URL_STEAM_CHARTS = 'https://steamcharts.com/app/238960'
URL_GIT_HYP = 'https://www.githyp.com/path-of-exile-100607/?tab=player-count'

SAVE_FILE = 'scraping_results.txt'

PAGE_LOADING_TIMEOUT = 30

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)
driver.set_page_load_timeout(PAGE_LOADING_TIMEOUT)

def print_to_file(list):
    with open(SAVE_FILE, "a+") as file:
        for item in list:
            file.write(item + ' ')
        file.write("\n")

def _get_webpage_html(url):
    try:
        driver.get(url)
        page_html = driver.page_source

        return page_html
    except:
        logging.error('Page loading timed out')
        return None


def get_poe_ninja_stats():
    page_html = _get_webpage_html(URL_POE_NINJA)
    if page_html is not None:
        soup = BeautifulSoup(page_html, "html.parser")
        div = soup.find("div", {"class": "stats-overview"})
        table = div.find("table")
        table_body = table.find('tbody')
        cells = [[td.text for td in row.findAll('td')] for row in table_body]
        return cells[0][1]
    else:
        return 'NONE'

def get_githyp_player_count():
    page_html = _get_webpage_html(URL_GIT_HYP)
    if page_html is not None:
        soup = BeautifulSoup(page_html, "html.parser")
        return soup.find("div", {"id": "player_val"}).text.replace(',', '')
    else:
        return 'NONE'

def get_steamcharts_player_count():
    page_html = _get_webpage_html(URL_STEAM_CHARTS)
    if page_html is not None:
        soup = BeautifulSoup(page_html, "html.parser")
        temp = soup.find("div", {"class": "app-stat"})
        temp = temp.find("span", {"class": "num"})
        return temp.text.replace(',', '')
    else:
        return 'NONE'

def periodic_scraping():
    last_scrape_time = datetime.now().time().minute - 1

    while True:

        now_time = datetime.now().time()

        if last_scrape_time != now_time.minute:
            last_scrape_time = now_time.minute

            res = [''] * 4

            res[0] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

            start_time_tot = time.time()
            logging.info('Scraping web pages ...')

            start_time = time.time()
            res[1] = get_poe_ninja_stats()
            end_time = time.time()
            logging.info('Poe.ninja scraped in {} seconds'.format(round(end_time - start_time, 2)))

            start_time = end_time
            res[2] = get_githyp_player_count()
            end_time = time.time()
            logging.info('GitHyp scraped in {} seconds'.format(round(end_time - start_time, 2)))

            start_time = end_time
            res[3] = get_steamcharts_player_count()
            end_time = time.time()
            logging.info('Steam Charts scraped in {} seconds'.format(round(end_time - start_time, 2)))

            end_time_tot = end_time
            logging.info('Web pages scraped in {} seconds'.format(round(end_time_tot - start_time_tot, 2)))

            logging.info('Results: {}'.format(res))

            print_to_file(res)

        time.sleep(1)

if __name__ == '__main__':
    t1 = threading.Thread(target=periodic_scraping)
    t1.start()
    t1.join()


    driver.quit()
