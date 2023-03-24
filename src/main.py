from pathlib import Path
import json
import pandas as pd
from tqdm import tqdm

def load_data(file):
    with file.open() as f:
        data = pd.read_csv(f)

    return data

def count_projects_ai_non_ai(organizations, data:pd.DataFrame):
    for row_index in tqdm(range(len(data))):
        row = data.iloc[row_index]
        full_name = row.get("full_name")
        org = full_name.split("/")[0]
        if org not in organizations:
            organizations[org] = {"count": 0, "ai_count": 0, "non_ai_count": 0}
        # print(row.get("frameworks"))
        # sleep(2)
        frameworks = row.get("frameworks")
        if isinstance(frameworks, str):
            organizations[org]["count"] += 1
            frmks = frameworks.replace("[", "").replace("]", "").replace("'", "")
            if frmks == "":
                organizations[org]["non_ai_count"] += 1
            else:
                frmks = frmks.split(", ")
                organizations[org]["ai_count"] += 1
                

def main():
    path = Path("data")
    organizations = {}
    for file in path.iterdir():
        if file.suffix == ".csv":
            data = load_data(file)
            count_projects_ai_non_ai(organizations, data)
            print(file)
    
    with open("data/stats.json", 'w') as file:
        json.dump(organizations, file)

    return organizations


if __name__ == "__main__":
    main()