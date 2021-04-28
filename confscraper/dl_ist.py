# %%
from glob import glob
from multiprocessing.pool import Pool
from time import strftime, strptime

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import confscraper as cs


# %%
def download_ist_volume(vol_num: int):
    """Download IST volume into pandas dataframe."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(
        "https://www.sciencedirect.com/journal/information-and-software-technology/vol/{}/suppl/C".format(
            vol_num
        )
    )
    date = driver.find_element_by_xpath("//h3[@class='js-issue-status text-s']").text
    if "(" in date:
        date = date[date.find("(") + 1 : date.find(")")]
    date = strftime("%Y%m", strptime(date, "%B %Y"))

    ignored_exceptions = (
        NoSuchElementException,
        StaleElementReferenceException,
    )
    driver.refresh()
    WebDriverWait(driver, 10, ignored_exceptions=ignored_exceptions).until(
        expected_conditions.presence_of_element_located((By.CLASS_NAME, "switch-check"))
    )
    driver.find_element_by_class_name("switch-check").click()

    previews = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "js-article-list-item"))
    )

    papers = []
    for p in previews:
        try:
            buttons = p.find_element_by_xpath(
                ".//ul[@class='tab-list']"
            ).find_elements_by_xpath(".//button")
            if len(buttons) > 0:
                buttons[0].click()
        except Exception as E:
            print(E)
            pass
        soup = BeautifulSoup(p.get_attribute("innerHTML"), features="html.parser")
        try:
            art_subtype = soup.find("span", {"class": "js-article-subtype"}).text
            art_title = soup.find("span", {"class": "js-article-title"}).text
            art_text = soup.find("div", {"class": "tab-panel"}).text
            papers.append(
                {
                    "title": "{} - {}".format(art_subtype, art_title),
                    "abstract": art_text,
                }
            )
        except Exception as e:
            print(e, soup.text)

    df = pd.DataFrame.from_records(papers)
    df["date"] = date

    return df


def vol_num_to_year(vol_num: int):
    """Get year from volume number."""
    year = 2021
    month = 9
    start = 137
    while True:
        if vol_num == start:
            return "{}%02d".format(year) % month
        start -= 1
        month -= 1
        if month == 0:
            month = 12
            year -= 1


# Download volumns
def download_and_save_ist(vol_num: int):
    """Download and save IST volumn."""
    completed = [
        i.split("_")[-1].split(".")[0]
        for i in glob(str(cs.external_dir() / "ist/*.csv"))
    ]
    if vol_num_to_year(vol_num) in completed:
        print("Already completed {}".format(vol_num))
        return None

    print("Downloading {}".format(vol_num))
    while True:
        try:
            df = download_ist_volume(vol_num)
        except Exception as E:
            print(E, "Retrying...")
        else:
            print("Completed {}".format(vol_num))
            break
    date = df.iloc[0]["date"]
    df = df[["title", "abstract"]]
    savedir = cs.get_dir(cs.external_dir() / "ist")
    df = df.replace(r"\n", " ", regex=True)
    df.to_csv(savedir / "ist_{}.csv".format(date), index=0)


# %% Download in parallel
with Pool(6) as p:
    for _ in p.imap_unordered(download_and_save_ist, range(138, 130, -1)):
        pass
