import requests
import json

def download_pubchem_json_with_requests(cid):
    """
    通过 PubChem CID 下载化合物的 JSON 数据。

    Args:
        cid (int): PubChem 化合物 ID。

    Returns:
        dict or None: 如果下载成功则返回 JSON 数据字典，否则返回 None。
    """
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/"
    try:
        response = requests.get(url, timeout=10) # 设置超时时间
        response.raise_for_status() # 如果请求失败，则抛出 HTTPError
        json_data = response.json()
        print(f"成功下载 CID {cid} 的 JSON 数据。")
        return json_data
    except requests.exceptions.RequestException as e:
        print(f"下载失败：{e}")
        return None

# 示例用法
compound_id = 2244  # 这是一个示例 CID，代表阿司匹林 (Aspirin)
json_data = download_pubchem_json_with_requests(compound_id)

if json_data:
    # 打印一些数据来验证
    print("\n部分数据预览：")
    print(f"化合物名称：{json_data['Record']['RecordTitle']}")
    print(f"分子式：{json_data['Record']['Section'][0]['Section'][0]['Information'][0]['Value']['StringWith(s)'][0]}")

# 如果需要将数据保存到文件
if json_data:
    filename = f"compound_{compound_id}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=4)
    print(f"\nJSON 数据已保存到文件：{filename}")