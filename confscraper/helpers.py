# %%
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm

import confscraper as cs


# %%
def scrape_conf_org(link: str, outputfile: str):
    """Scrape from conf layout websites."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(link)
    webpage = driver.page_source
    soup = BeautifulSoup(webpage, features="html.parser")

    pt = soup.find("h3", string="Accepted Papers")
    table = pt.find_next_sibling()
    links = [
        i
        for i in table.find_all("a")
        if "href" in i.attrs and "javascript:eventModal" in i.attrs["href"]
    ]

    papers = []
    for link in tqdm(links):
        script = link.attrs["href"]
        driver.execute_script(script)
        id = script[23:-2].replace("mdl", "modal")
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.ID, id))
        )
        title = (
            driver.find_element_by_id(id).find_element_by_class_name("modal-title").text
        )
        abstract = (
            driver.find_element_by_id(id)
            .find_element_by_class_name("modal-body")
            .find_elements_by_css_selector("p")
        )
        abstract = "\n".join([i.text for i in abstract])
        papers.append({"title": title, "abstract": abstract})
    pd.DataFrame.from_records(papers).replace(r"\n", " ", regex=True).to_csv(
        cs.external_dir() / outputfile, index=0
    )


# %%
def scrape_esec_fse_2019(link: str, outputfile: str):
    """Scrape from esec_fse_2019 layout websites."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(link)
    webpage = driver.page_source
    soup = BeautifulSoup(webpage, features="html.parser")
    pt = soup.find("h2", string="List of accepted papers of the main research track:")
    pt = pt.find_next_sibling()
    papers = []
    while True:
        title = pt.find("span", {"style": "font-size: 100%"}).text.strip()
        abstract = pt.find(
            "span",
            {
                "style": "display:none; border:1ex solid transparent; font-size: smaller;"
            },
        ).text.strip()
        papers.append({"title": title, "abstract": abstract})
        pt = pt.find_next_sibling()
        if not pt:
            break
    pd.DataFrame.from_records(papers).replace(r"\n", " ", regex=True).to_csv(
        cs.external_dir() / outputfile, index=0
    )
