import os
import shutil
import re
import hashlib
import urllib.parse
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
        "action": "parse",
        "page": operator_name,
        "format": "json"
    }

    res = requests.get(API_URL, params=params).json()
    html = res["parse"]["text"]["*"]
    soup = BeautifulSoup(html, "html.parser")

    # turn soup back into a string
    html_str = str(soup)

    pattern = r'/w/%E6%96%87%E4%BB%B6:(%E6%8A%80%E8%83%BD_[^"\s<>]+?\.png)'
    matches = re.findall(pattern, html_str)

    results = []
    for fname_encoded in matches:
        # decode filename for hashing
        fname = urllib.parse.unquote(fname_encoded)

        skill_name = fname.replace("技能_", "").replace(".png", "")

        md5 = hashlib.md5(fname.encode("utf-8")).hexdigest()
        # build proper thumb URL
        url = f"https://media.prts.wiki/{md5[0]}/{md5[0:2]}/{fname_encoded}"
        results.append((url, skill_name))

    # remove duplicates
    results = list(dict.fromkeys(results))

    skill_idx = 0
    for url, skill_name in results:
            skill_idx += 1

            filename = os.path.join(SAVE_DIR, f"{operator_name}_{skill_idx}.png")

            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(filename, "wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"Saved skill {skill_idx} {skill_name} for {operator_name}")
            else:
                print("Failed to download image:", response.status_code)
    
    if (skill_idx == 0):
        print("No skills found for", operator_name)

if os.path.exists(SAVE_DIR):
    shutil.rmtree(SAVE_DIR)

os.makedirs(SAVE_DIR, exist_ok=True)

operators = extract_operator_names("干员一览")

for operator in operators:
    extract_skill_info(operator)