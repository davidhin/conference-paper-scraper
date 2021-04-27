# %%
import confscraper.helpers as csh

# %% ICSE
csh.scrape_conf_org(
    "https://2020.icse-conferences.org/track/icse-2020-papers?#event-overview",
    "icse_2020.csv",
)

csh.scrape_conf_org(
    "https://2019.icse-conferences.org/track/icse-2019-Technical-Papers?#event-overview",
    "icse_2019.csv",
)

csh.scrape_conf_org(
    "https://www.icse2018.org/track/icse-2018-Technical-Papers?#event-overview",
    "icse_2018.csv",
)

# %% ASE
csh.scrape_conf_org(
    "https://conf.researchr.org/track/ase-2020/ase-2020-papers?#event-overview",
    "ase_2020.csv",
)

csh.scrape_conf_org(
    "https://2019.ase-conferences.org/track/ase-2019-papers?#event-overview",
    "ase_2019.csv",
)

# %% MSR
csh.scrape_conf_org(
    "https://2018.msrconf.org/track/msr-2018-papers", "msr_2018.csv",
)

# %% FSE
csh.scrape_conf_org(
    "https://2020.esec-fse.org/track/fse-2020-papers?#event-overview",
    "esec-fse_2020.csv",
)

csh.scrape_esec_fse_2019(
    "https://esec-fse19.ut.ee/program/research-papers/", "esec-fse_2019.csv"
)

csh.scrape_conf_org(
    "https://2018.fseconference.org/track/fse-2018-research-papers?#event-overview",
    "fse_2018.csv",
)

# %% ISSTA
csh.scrape_conf_org(
    "https://conf.researchr.org/track/issta-2020/issta-2020-papers#event-overview",
    "issta_2020.csv",
)

csh.scrape_conf_org(
    "https://conf.researchr.org/track/issta-2019/issta-2019-Technical-Papers#event-overview",
    "issta_2019.csv",
)

csh.scrape_conf_org(
    "https://conf.researchr.org/track/issta-2018/issta-2018-Technical-Papers",
    "issta_2018.csv",
)

# %% ICST
csh.scrape_conf_org(
    "https://icst2020.info/track/icst-2020-papers?#event-overview", "icst_2020.csv",
)
