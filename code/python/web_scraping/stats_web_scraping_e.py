import time
import threading
from datetime import datetime, timedelta

import logging

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from pyvirtualdisplay import Display


URL_POE_NINJA = 'https://poe.ninja/stats'
URL_STEAM_CHARTS = 'https://steamcharts.com/app/238960'
URL_GIT_HYP = 'https://www.githyp.com/path-of-exile-100607/?tab=player-count'

SAVE_FILE = 'scraping_results_e.txt'

TEST_MODE = False
PAGE_LOADING_TIMEOUT = 60

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

class WebBrowsingSession:
    def __init__(self):
        # selenium driver options
        self.options = Options()
        self.options.headless = True

        self.active_inst = False

    def instance_browser(self):
        if self.active_inst:
            raise ValueError('Web driver instance already active')

        # monitor display configuration
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()

        self.driver = webdriver.Firefox(options=self.options)
        self.driver.set_page_load_timeout(PAGE_LOADING_TIMEOUT)

        self.active_inst = True

    def release_browser(self):
        if not self.active_inst:
            raise ValueError('No web driver instance active')

        self.driver.quit()

        self.display.popen.terminate()

        self.active_inst = False

    def get_webpage_html(self, url):
        if not self.active_inst:
            raise ValueError('No web driver instance active')
        try:
            self.driver.get(url)
            res = self.driver.page_source
        except:
            logging.error('Page loading timed out')
            res = None
        finally:
            return res

def write_to_file(list, file_path):
    with open(file_path, "a+") as file:
        file.write(list[0].strftime("%m/%d/%Y %H:%M:%S") + ' ')
        for item in list[1:]:
            file.write(item + ' ')

        file.write("\n")

def get_poe_ninja_stats(wsession):
    page_html = wsession.get_webpage_html(URL_POE_NINJA)
    try:
        soup = BeautifulSoup(page_html, "html.parser")
        div = soup.find("div", {"class": "stats-overview"})
        table = div.find("table")
        table_body = table.find('tbody')
        cells = [[td.text for td in row.findAll('td')] for row in table_body]
        return cells[0][1]
    except:
        return 'NONE'

def get_githyp_player_count(wsession):
    page_html = wsession.get_webpage_html(URL_GIT_HYP)
    try:
        soup = BeautifulSoup(page_html, "html.parser")
        return soup.find("div", {"id": "player_val"}).text.replace(',', '')
    except:
        return 'NONE'

def get_steamcharts_player_count(wsession):
    page_html = wsession.get_webpage_html(URL_STEAM_CHARTS)
    try:
        soup = BeautifulSoup(page_html, "html.parser")
        temp = soup.find("div", {"class": "app-stat"})
        temp = temp.find("span", {"class": "num"})
        return temp.text.replace(',', '')
    except:
        return 'NONE'

def periodic_scraping():
    logging.info('Starting script with test mode {}'.format('ON' if TEST_MODE else 'OFF'))

    wsession = WebBrowsingSession()

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

        res = list()

        res.append(datetime.now())

        wsession.instance_browser()

        start_time = time.time()
        res.append(get_poe_ninja_stats(wsession))
        end_time = time.time()
        logging.info('Poe.ninja scraped in {} seconds'.format(round(end_time - start_time, 2)))

        start_time = end_time
        res.append(get_githyp_player_count(wsession))
        end_time = time.time()
        logging.info('GitHyp scraped in {} seconds'.format(round(end_time - start_time, 2)))

        start_time = end_time
        res.append(get_steamcharts_player_count(wsession))
        end_time = time.time()
        logging.info('Steam Charts scraped in {} seconds'.format(round(end_time - start_time, 2)))

        wsession.release_browser()

        logging.info('Results: {}'.format(res))

        end_time_tot = end_time
        logging.info('Web pages scraped in {} seconds'.format(round(end_time_tot - start_time_tot, 2)))

        # save scraped data
        write_to_file(res, SAVE_FILE)

if __name__ == '__main__':

    t1 = threading.Thread(target=periodic_scraping)
    t1.start()
