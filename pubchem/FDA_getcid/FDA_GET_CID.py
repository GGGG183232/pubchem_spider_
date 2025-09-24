import pandas as pd
import json
import json
import requests
from tqdm import tqdm
import csv

# 从药名提取cid
def get_cid(name: str):
    base_url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{}/property/CanonicalSMILES,title/JSON'
    headers = {"content-type": "application/x-www-form-urlencoded"}
    url = base_url.format(name)
    res = requests.get(url, headers=headers)
    try:
        data_dict = json.loads(res.text)
        cid = data_dict['PropertyTable']['Properties'][0]["CID"]
        smiles = data_dict['PropertyTable']['Properties'][0]["ConnectivitySMILES"]

    except:
        return None
    return cid


# 文件路径，使用原始字符串 (r"...") 来避免转义字符问题
file_path = r"E:\PROJECT\25_71_Robinagent\spider\pubchem\pubchem_scrapy\pubchem_scrapy1\FDA_getcid\FDA_JSON.json"

# 打开json并读取json
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)  # 根据json的格式读取，读出来是

results_list = data['results']  # 读取data的result字段是一个list

all_active_ingredients = []
dict = {}
data_to_write = []
for i in tqdm(range(len(results_list))):  # 里面每个durg又是一个dict
    if i > 100:
        break
    drug = results_list[i]
    if 'active_ingredients' in drug:
        drugname = drug['active_ingredients'][0]['name']
        all_active_ingredients.append(drugname)
        cid = get_cid(drugname)
        if cid == None:
            continue
        else:
            dict[drugname] = cid    # 存在dict里，键是药名值是cid
            data_to_write.append([drugname, cid])


with open(r"E:\PROJECT\25_71_Robinagent\spider\pubchem\pubchem_scrapy\pubchem_scrapy1\FDA_getcid\fda2cas.csv", 'w',
          newline='', encoding='utf-8-sig') as file:
    # 1. 创建 writer 对象
    writer = csv.writer(file)

    # 2. 使用 writerows() 方法传入列表一次性写入多行
    writer.writerows(data_to_write)

# 7. 打印所有提取到的活性成分
print("成功提取所有药物的活性成分:")
for i in range(len(results_list)):
    print(all_active_ingredients[i] + dict[all_active_ingredients[i]])
print(json.dumps(all_active_ingredients, indent=2, ensure_ascii=False))
