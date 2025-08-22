import os
import requests
from bs4 import BeautifulSoup

API_URL = "https://prts.wiki/api.php"
SAVE_DIR = "./skills/"

def extract_operator_names(operator_list_title):
    params = {
        "action": "parse",
        "page": operator_list_title,
        "format": "json"
    }
    res = requests.get(API_URL, params=params).json()
    html = res["parse"]["text"]["*"]
    soup = BeautifulSoup(html, "html.parser")

    # find the hidden container
    filter_data_div = soup.find("div", {"id": "filter-data"})

    records = []
    for entry in filter_data_div.find_all("div", recursive=False):  # only direct children
        record = entry.attrs  # all data-* attributes as a dictionary
        records.append(record)

    extracted = []
    for r in records:
        extracted.append(r["data-zh"])

    return extracted

def extract_skill_info(operator_name):
    print(f"Extracting skills for operator: {operator_name}")

    params = {
        "action": "query",
        "titles": operator_name,
        "generator": "images",
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json"
    }
    res = requests.get(API_URL, params=params).json()
    
    skill_idx = 1
    for page in res.get("query", {}).get("pages", {}).values():
        if "imageinfo" in page:
            if "技能" in page["title"]:
                skill_name = page["title"].replace("文件:技能 ", '').replace(".png", '')

                filename = os.path.join(SAVE_DIR, f"{operator_name}_{skill_idx}_{skill_name}.png")

                response = requests.get(page["imageinfo"][0]["url"], stream=True)
                if response.status_code == 200:
                    with open(filename, "wb") as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                    print(f"Saved image as {filename}")
                else:
                    print("Failed to download image:", response.status_code)

                skill_idx += 1

os.makedirs(SAVE_DIR)

operators = extract_operator_names("干员一览")

for operator in operators:
    extract_skill_info(operator)