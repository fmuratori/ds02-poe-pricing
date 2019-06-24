import os

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from bs4 import BeautifulSoup

from .. import constants 

print(constants.URL_POE_NINJA)

def get_web_page_tree(url):
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(
        options=options,
        executable_path=BROWSER_DRIVE)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    return soup


def get_stats_from_webpage():
    soup = get_web_page_tree(URL_POE_NINJA)
    mydivs = soup.find_all("table")

def get_player_count_steamcharts():
    soup = get_web_page_tree(URL_STEAM_CHARTS)

def get_player_count_githyp():
    soup = get_web_page_tree(URL_GIT_HYP)


if __name__ == '__main__':
    # get stats
    get_stats_from_webpage()
    # save stats

    # get player count
    # save player count
