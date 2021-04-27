# %%
from glob import glob

import pandas as pd

import confscraper as cs

# Generate table html
all_dfs = []
for csv in glob(str(cs.external_dir() / "**/*.csv"), recursive=True):
    conf, year = csv.split("/")[-1].split(".")[0].split("_")[0:2]
    temp_df = pd.read_csv(csv)
    temp_df["conference"] = conf
    temp_df["year"] = year
    temp_df["num_published"] = len(temp_df)
    all_dfs.append(temp_df)
df = pd.concat(all_dfs)
df = df.sort_values(["year"], ascending=0)

html_string = """
<html>
  <link rel="stylesheet" type="text/css" href="{stylecss}"/>
  <body>
    <div class="container">
        <div class="fixed">
            <span style="font-size:30pt">Papers</span>
            {table}
        </div>
    </div>
  </body>
</html>.
"""

# Filtering
base = r"^{}"
expr = "(?=.*{})"
words = [""]
search_string = base.format("".join(expr.format(w) for w in words))
df = df[
    df.title.str.contains(r"{}".format(search_string), case=False, regex=True)
    | df.abstract.str.contains(r"{}".format(search_string), case=False, regex=True)
]
df = df[df.conference != "iswc"]


# OUTPUT AN HTML FILE
with open(cs.outputs_dir() / "table.html", "w") as f:
    f.write(
        html_string.format(
            stylecss=cs.external_dir() / "df_style.css",
            table=df.to_html(classes="mystyle"),
        )
    )


# %%
