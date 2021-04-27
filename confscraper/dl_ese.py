# %%
from glob import glob
from multiprocessing.pool import Pool
from time import strftime, strptime

import pandas as pd
import requests
from bs4 import BeautifulSoup

import confscraper as cs


# %% Helper functions
def download_issue(issue):
    """Download issue given issue object.

    Issue object example:
    ['/journal/10664/volumes-and-issues/26-4', 'July 2021, issue 4']
    """
    link = issue[0]
    issue_name = issue[1]
    issue = requests.get("https://link.springer.com" + link)
    issue_soup = BeautifulSoup(issue.text, features="html.parser")
    papers = issue_soup.find("div", {"id": "main-content"}).find_all(
        "h3", {"class": "c-card__title"}
    )
    papers = [p.find("a") for p in papers]
    papers = [
        {"link": i.attrs["href"], "title": i.text, "issue": issue_name} for i in papers
    ]
    return papers


def get_abstract(paper):
    """Return paper object with abstract given a paper object."""
    link = paper["link"]
    try:
        abstract = (
            BeautifulSoup(requests.get(link).text, features="html.parser")
            .find("div", {"id": "Abs1-content"})
            .text
        )
        paper["abstract"] = abstract
    except Exception as E:
        print(E, " - ", paper["title"])
    return paper


def issue_to_ymd(s: str):
    """Convert issue string to year-month-day."""
    return strftime("%Y%m%d", strptime(s, "%B %Y, issue %d"))


# %% Get Issues
links = requests.get("https://link.springer.com/journal/10664/volumes-and-issues")
links_soup = BeautifulSoup(links.text, features="html.parser")
volumes = links_soup.find_all("li", {"class": "app-section"})
volumes = volumes[:6]
issues = []
completed = [
    i.split("_")[-1].split(".")[0] for i in glob(str(cs.external_dir() / "ese/*.csv"))
]
for v in volumes:
    list_items = v.find_all("li", {"class": "c-list-group__item"})
    list_items = [li.find("a") for li in list_items]
    for i in list_items:
        if issue_to_ymd(i.text) in completed:
            print("Already downloaded {}".format(i.text))
            continue
        issues.append([i.attrs["href"], i.text])

# %% Get papers
papers_no_abstract = []
progress = 0
if len(issues) > 0:
    with Pool(min(len(issues), 4)) as p:
        for i in p.imap_unordered(download_issue, issues):
            papers_no_abstract += i
            progress += 1
            print(progress)

# %% Download papers in parallel
if len(papers_no_abstract) > 0:
    papers_with_abstract = []
    progress = 0
    with Pool(min(len(papers_no_abstract), 4)) as p:
        for i in p.imap_unordered(get_abstract, papers_no_abstract):
            papers_with_abstract.append(i)
            progress += 1
            print(i["issue"], progress)

    # Get dataframe
    df = pd.DataFrame.from_records(papers_with_abstract)
    df.issue = df.issue.apply(issue_to_ymd)
    df = df.sort_values("issue", ascending=0)
    for issue in df.issue.drop_duplicates():
        df_temp = df[df.issue == issue]
        savedir = cs.get_dir(cs.external_dir() / "ese")
        df_temp = df_temp[["title", "abstract"]]
        df_temp = df_temp.replace(r"\n", " ", regex=True)
        df_temp.to_csv(savedir / "ese_{}.csv".format(issue), index=0)
