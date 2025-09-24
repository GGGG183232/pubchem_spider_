import pandas
import pandas as pd
import requests
import json
import time
from tqdm import tqdm


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
        return None, None
    return cid, smiles


def process_drug_csv(file_path: str):
    """
    读取CSV文件，获取drug_name，查询CID和SMILES，并写回文件。
    """
    print(f"正在读取文件: {file_path}")
    try:
        # 使用 pandas 读取 CSV 文件
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"错误：文件未找到，请检查路径是否正确: {file_path}")
        return
    except Exception as e:
        print(f"读取文件时发生未知错误: {e}")
        return

    # 检查 'drug_name' 列是否存在
    if 'drug_name' not in df.columns:
        print(f"错误：文件中未找到 'drug_name' 列。")
        return

    # 创建两个空列表来存储将要获取的数据
    cids = []
    smiles_list = []

    print("开始从 PubChem 获取 CID 和 SMILES...")
    # 使用tqdm来显示进度条，遍历 'drug_name' 列
    for drug_name in tqdm(df['drug_name'], desc="正在处理"):
        if pd.isna(drug_name) or not isinstance(drug_name, str) or drug_name.strip() == "":
            # 如果药品名称为空或无效，则直接添加空值
            cid, smiles = None, None
        else:
            # 调用函数获取数据
            cid, smiles = get_cid(drug_name)
            # 为了遵守PubChem API的使用规则（不超过每秒5次请求），增加一个小的延时
            time.sleep(0.21)

        # 将获取到的结果（可能是None）添加到列表中
        if cid == None:
            cids.append(None)
            smiles_list.append(None)
        else:
            cids.append(int(cid))
            smiles_list.append(smiles)

    # 将两个列表作为新列添加到DataFrame中
    print("\n数据获取完成，正在添加到CSV中...")
    df['cid'] = cids
    df['smiles'] = smiles_list

    try:
        # 将更新后的DataFrame写回原始的CSV文件
        # index=False 表示在写入CSV时不包含DataFrame的索引列
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"处理成功！数据已更新并保存回原文件: {file_path}")
        print("\n更新后数据的前5行预览：")
        print(df.head())
    except Exception as e:
        print(f"保存文件时发生错误: {e}")


# --- 主程序入口 ---
if __name__ == "__main__":
    # 请在这里修改为您的CSV文件的确切路径
    # 使用原始字符串 (r'...') 来避免Windows路径中反斜杠的问题
    csv_file_path = r'E:\PROJECT\25_71_Robinagent\spider\pubchem\pubchem_scrapy\pubchem_scrapy1\20250915_095558.csv'

    process_drug_csv(csv_file_path)
