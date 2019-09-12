import time
import threading
from datetime import datetime, timedelta

import logging

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from pyvirtualdisplay import Display

TEST_MODE = False

URL_POE_NINJA = 'https://poe.ninja/stats'
URL_STEAM_CHARTS = 'https://steamcharts.com/app/238960'
URL_GIT_HYP = 'https://www.githyp.com/path-of-exile-100607/?tab=player-count'

SAVE_FILE = 'scraping_results.txt'

PAGE_LOADING_TIMEOUT = 60

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

display = Display(visible=0, size=(800, 600))
display.start()

# selenium driver options
options = Options()
options.headless = True

driver = webdriver.Firefox(options=options)
driver.set_page_load_timeout(PAGE_LOADING_TIMEOUT)

def get_webpage_html(url):
    try:
        driver.get(url)
        res = driver.page_source
    except:
        logging.error('Page loading timed out')
        res = None
    return res

def print_to_file(list):
    with open(SAVE_FILE, "a+") as file:
        file.write(list[0].strftime("%m/%d/%Y %H:%M:%S") + ' ')
        for item in list[1:]:
            file.write(item + ' ')

        file.write("\n")

def get_poe_ninja_stats():
    page_html = get_webpage_html(URL_POE_NINJA)
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
    page_html = get_webpage_html(URL_GIT_HYP)
    if page_html is not None:
        soup = BeautifulSoup(page_html, "html.parser")
        return soup.find("div", {"id": "player_val"}).text.replace(',', '')
    else:
        return 'NONE'

def get_steamcharts_player_count():
    page_html = get_webpage_html(URL_STEAM_CHARTS)
    if page_html is not None:
        soup = BeautifulSoup(page_html, "html.parser")
        temp = soup.find("div", {"class": "app-stat"})
        temp = temp.find("span", {"class": "num"})
        return temp.text.replace(',', '')
    else:
        return 'NONE'

def periodic_scraping():
    logging.info('Starting script with test mode {}'.format('ON' if TEST_MODE else 'OFF'))

    while True:
        if not TEST_MODE:
            # syncronie with new hour time
             now_datetime = datetime.now()
             temp = now_datetime + timedelta(hours=1)
             next_hour_datetime = datetime(temp.year, temp.month, temp.day, temp.hour, 0, 0, 0)
             time_delta = next_hour_datetime - now_datetime
             sleep_seconds = time_delta.seconds + 1

             logging.info('Sleeping for {} seconds from {} to {}'.format(sleep_seconds, str(now_datetime), str(next_hour_datetime)))
             time.sleep(sleep_seconds)

        # scrape data
        start_time_tot = time.time()
        logging.info('Scraping web pages ...')

        res = [''] * 4

        res[0] = datetime.now()

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

        logging.info('Results: {}'.format(res))

        end_time_tot = end_time
        logging.info('Web pages scraped in {} seconds'.format(round(end_time_tot - start_time_tot, 2)))

        # save scraped data
        print_to_file(res)

if __name__ == '__main__':
    t1 = threading.Thread(target=periodic_scraping)
    t1.start()
    t1.join()
