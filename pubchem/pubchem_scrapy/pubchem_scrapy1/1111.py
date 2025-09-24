import csv
import pandas as pd
import  os
import json
import requests
input1 = r"E:\PROJECT\25_71_Robinagent\spider\pubchem\pubchem_scrapy\pubchem_scrapy1\20250915_095558.csv"
def get_cid(name: str):
    base_url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{}/property/title/CSV'
    headers = {"content-type": "application/x-www-form-urlencoded"}
    url = base_url.format(name)
    res = requests.get(url, headers=headers)
    data_lines = res.text.strip().split('\n')[1:]
    cid = res.text.strip().split('\n')[1:]
    smiles = res.text.strip().split('\n')[1:][4]
    return cid,smiles


df = pd.read_csv(input1)
drug_name_column = df['drug_name']
for drug_name in drug_name_column:
    cid = get_cid(drug_name)

