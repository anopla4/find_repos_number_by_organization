from pathlib import Path
import json
import pandas as pd
from tqdm import tqdm
import numpy as np
import time


def load_data(file):
    with file.open() as f:
        data = pd.read_csv(f)

    return data


def count_projects_ai_non_ai(organizations, data: pd.DataFrame):
    for row_index in tqdm(range(len(data))):
        row = data.iloc[row_index]
        full_name = row.get("full_name")
        org = full_name.split("/")[0]
        if org not in organizations:
            organizations[org] = {
                "count": 0,
                "ai_count": {"count": 0, "frameworks": []},
                "non_ai_count": 0,
            }
        frameworks = row.get("frameworks")
        if isinstance(frameworks, str):
            organizations[org]["count"] += 1
            frmks = frameworks.replace("[", "").replace("]", "").replace("'", "")
            if frmks == "":
                organizations[org]["non_ai_count"] += 1
            else:
                frmks = frmks.split(", ")
                organizations[org]["ai_count"]["count"] += 1
                organizations[org]["ai_count"]["frameworks"] = list(
                    set(organizations[org]["ai_count"]["frameworks"] + frmks)
                )


def projects_table(data, lang):
    rows = []
    for row_index in tqdm(range(len(data))):
        row = data.iloc[row_index]
        full_name = row.get("full_name").split("/")
        name = full_name[-1]
        org = full_name[0]
        frameworks = row.get("frameworks")
        libs = []
        if isinstance(frameworks, str):
            temp = frameworks.replace("[", "").replace("]", "").replace("'", "")
            if len(temp):
                libs = temp.split(", ")
        rows.append([name, org, lang, libs, 1, 1 if len(libs) else 0])
    return rows


def main():
    path = Path("data")
    rows = []
    for file in path.iterdir():
        if file.suffix == ".csv" and file.stem.startswith("output"):
            data = load_data(file)
            rows += projects_table(data, file.stem.split("_")[-1])
            # count_projects_ai_non_ai(organizations, data)
    table = pd.DataFrame(
        rows,
        columns=[
            "Name",
            "Organization",
            "Language",
            "AI-libraries",
            "Count",
            "AI_count",
        ],
    )
    grouped_by_organization = table.groupby(by=["Organization"]).sum()
    organizations_temp = []
    for r in grouped_by_organization.index:
        row = grouped_by_organization.loc[r]
        count = row.get("Count")
        ai_count = row.get("AI_count")
        if count > 100 and ai_count:
            organizations_temp.append((r, ai_count))
    top_5 = sorted(organizations_temp, key=lambda x: -x[1])[:5]
    top_5 = [s[0] for s in top_5]
    filter = (
        (table["Organization"] == top_5[0])
        | (table["Organization"] == top_5[1])
        | (table["Organization"] == top_5[2])
        | (table["Organization"] == top_5[3])
        | (table["Organization"] == top_5[4])
    )
    filter_orgs = (
        table.where(filter)
        .dropna(axis=0)
        .filter(items=["Name", "Organization", "Language", "AI-libraries"])
        .reset_index(drop=True)
    )
    filter_orgs.to_csv("data/projects.csv")
    # with open("data/stats.json", 'w') as file:
    #     json.dump(organizations, file)


if __name__ == "__main__":
    main()
