# %%

from multiprocessing.pool import Pool

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm

import confscraper as cs

# %% Springer
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
papers = {}
books = [
    "https://link.springer.com/book/10.1007/978-3-030-62419-4",
    "https://link.springer.com/book/10.1007/978-3-030-62466-8",
    "https://link.springer.com/book/10.1007/978-3-030-30793-6",
    "https://link.springer.com/book/10.1007/978-3-030-30796-7",
    "https://link.springer.com/book/10.1007/978-3-030-00671-6",
    "https://link.springer.com/book/10.1007/978-3-030-00668-6",
    "https://link.springer.com/book/10.1007/978-3-319-68288-4",
    "https://link.springer.com/book/10.1007/978-3-319-68204-4",
]

for book in tqdm(books):
    page = 1
    while True:
        driver.get("{}?page={}".format(book, page))
        webpage = driver.page_source
        soup = BeautifulSoup(webpage, features="html.parser")
        conf_name = soup.find("h1").text
        max_page = int(soup.find("span", {"class": "test-maxpagenum"}).text)
        pt = soup.find("div", {"id": "booktoc"})
        tracks = soup.find_all("h3", {"class": "content-type-list__subheading"})
        for track in tracks:
            t = track.find_next_sibling()
            trackname = track.text
            links = t.find_all("li", {"class": "chapter-item content-type-list__item"})
            for link in links:
                title = link.find("a").text
                papers[conf_name + "||" + trackname + "||" + title] = link.find(
                    "a"
                ).attrs["href"]
        page += 1
        if page > max_page:
            break
    print(len(papers))


def get_abstract_from_springer(paper):
    """Return title and abstract given a paper object.

    Example object:
    ('Computing Compliant Anonymisations...', '/chapter/10.1007/978-3-030-62419-4_1')
    """
    title = paper[0]
    link = paper[1]
    if link[0] != "/":
        return
    paper_soup = BeautifulSoup(
        requests.get("https://link.springer.com{}".format(link)).text,
        features="html.parser",
    )
    abstract = paper_soup.find("p", {"id": "Par1"}).text
    return [title, abstract]


# %% Parallel Download Abstracts
df_rows = []
progress = 0
with Pool(24) as p:
    for row in p.imap_unordered(get_abstract_from_springer, papers.items()):
        progress += 1
        print(progress)
        df_rows.append(row)

# %% Save files
df = pd.DataFrame(df_rows, columns=["title", "abstract"])
df["year"] = df.title.apply(lambda x: "".join(x.split("||")[0].split()[-1]))
df["title"] = df.title.apply(lambda x: " - ".join(x.split("||")[1:]))
for year in df.year.drop_duplicates():
    df[df.year == year].replace(r"\n", " ", regex=True).to_csv(
        cs.external_dir() / "iswc_{}.csv".format(year), index=0
    )
