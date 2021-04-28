from datetime import datetime
from multiprocessing.pool import Pool

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import confscraper as cs

# %% Generate dates
dates = []
year = 2021
month = datetime.today().month
while True:
    dates.append([year, month])
    month -= 1
    if month == 0:
        year -= 1
        month = 12
    if year == 2016:
        break


def get_papers_no_abstract(date):
    """Get papers from TSE given year and month in tuple [2021, 12]."""
    year = date[0]
    month = date[1]
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.computer.org/csdl/journal/ts/{}/%02d".format(year) % month)
    articles = driver.find_elements_by_xpath("//a[@class='article-title']")
    papers = [
        {
            "link": a.get_attribute("href"),
            "title": a.text,
            "issue": "{}%02d".format(year) % month,
        }
        for a in articles
    ]
    return papers


# %% Download papers no abstract
papers_no_abstract = []
progress = len(dates)
with Pool(8) as p:
    for i in p.imap_unordered(get_papers_no_abstract, dates):
        papers_no_abstract += i
        progress -= 1
        print(progress)

# %% Download abstracts of papers
papers_no_abstract = pd.read_csv("papers_no_abstract.csv").to_dict(orient="records")


def get_paper_abstracts(paper):
    """Get paper abstracts."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(paper["link"])
    abstract = " ".join(
        [
            i.text
            for i in driver.find_elements_by_xpath(
                "//div[contains(@class, 'article-content')]"
            )
        ]
    ).strip()
    try:
        keywords = driver.find_element_by_xpath("//csdl-article-keywords").text
        abstract += keywords
    except Exception as E:
        print(E)
        pass
    paper["abstract"] = abstract
    return paper


# %% Get paper abstracts
papers_with_abstract = []
progress = len(papers_no_abstract)
with Pool(5) as p:
    for i in p.imap_unordered(get_paper_abstracts, papers_no_abstract):
        papers_with_abstract.append(i)
        progress -= 1
        print(progress)


# %% Save dataframes
pwa_df_orig = pd.DataFrame(papers_with_abstract)
for issue in pwa_df_orig.issue.drop_duplicates():
    df_temp = pwa_df_orig[pwa_df_orig.issue == issue]
    savedir = cs.get_dir(cs.external_dir() / "tse")
    df_temp = df_temp[["title", "abstract"]]
    df_temp = df_temp.replace(r"\n", " ", regex=True)
    df_temp.to_csv(savedir / "tse_{}.csv".format(issue), index=0)
