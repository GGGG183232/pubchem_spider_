import requests
import json
import re
import urllib.parse
import time
import os

# --- 全局变量用于缓存 ---
processed_nodes = set()  # 存储已经访问过的分类节点 ID。
cid_cache = {}  # 缓存药品名称到其 PubChem CID 的映射。
# all_drugs_catalog 不再作为全局列表收集所有数据，而是直接写入文件

# --- 配置 ---
API_REQUEST_DELAY_SECONDS = 0.2  # 定义每次 API 请求之间的延迟时间（秒）。
REQUEST_TIMEOUT_SECONDS_CID = 30  # 获取 PubChem CID 请求的超时时间（秒）。
REQUEST_TIMEOUT_SECONDS_DETAILS = 30  # 获取药物详细信息请求的超时时间（秒）。
REQUEST_TIMEOUT_SECONDS_CLASSIFICATION = 30  # 获取分类数据请求的超时时间（秒）。

# 药品目录文件路径
DRUG_CATALOG_FILENAME = r"E:\PROJECT\25_71_Robinagent\spider\pubchem\drug_cataloge\drug_catalogue.json"

# 用于控制 JSON 数组的第一个元素前是否需要逗号
is_first_entry = True


# --- 函数：根据药品名称获取 PubChem CID ---
def get_pubchem_cid(drug_name):
    """
    根据药品名称获取 PubChem CID。
    缓存结果以避免重复的 API 调用。
    返回找到的第一个 CID，如果未找到则返回 None。
    """
    if drug_name and drug_name in cid_cache:
        return cid_cache[drug_name]

    pubchem_cid_found = None
    if drug_name:
        encoded_drug_name = urllib.parse.quote(drug_name)
        pug_rest_url_name = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{encoded_drug_name}/cids/JSON"
        try:
            response_name = requests.get(pug_rest_url_name, timeout=REQUEST_TIMEOUT_SECONDS_CID)
            response_name.raise_for_status()

            data_name = response_name.json()
            if "IdentifierList" in data_name and "CID" in data_name["IdentifierList"] and data_name["IdentifierList"][
                "CID"]:
                pubchem_cid_found = data_name["IdentifierList"]["CID"][0]
                cid_cache[drug_name] = pubchem_cid_found
                return pubchem_cid_found
            else:
                print(f"警告: PubChem 未为名称 '{drug_name}' 返回任何 CID。")
        except requests.exceptions.RequestException as e:
            print(f"错误: 名称 '{drug_name}' CID 查询时发生网络错误: {e}")
        time.sleep(API_REQUEST_DELAY_SECONDS)

    if drug_name:
        cid_cache[drug_name] = None
    return None


# --- 函数：获取 PubChem 化合物的原始详细信息 JSON (使用 PUG-View API) ---
def get_pubchem_compound_raw_json(pubchem_cid):
    """
    根据给定的 PubChem CID 获取完整的原始 JSON 描述信息 (使用 PUG-View API)。
    返回原始 JSON 数据（字典），如果获取失败则返回 None。
    """
    details_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{pubchem_cid}/JSON/?response_type=display"
    try:
        response = requests.get(details_url, timeout=REQUEST_TIMEOUT_SECONDS_DETAILS)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"错误: 获取 PubChem CID {pubchem_cid} 的原始详细信息 (PUG-View) 失败: {e}")
        return None
    finally:
        time.sleep(API_REQUEST_DELAY_SECONDS)


# --- 从 PubChem 原始 JSON 中提取 INN 和 CAS ---
def extract_inn_cas_and_english_name(raw_json_data):
    """
    从 PubChem PUG-View 原始 JSON 数据中提取 INN、CAS 号和主要英文名。
    """
    inn = None
    cas_number = None
    english_name = None

    if "Record" in raw_json_data:
        record = raw_json_data["Record"]

        if "RecordTitle" in record:
            english_name = record["RecordTitle"]

        if "Section" in record:
            for section in record["Section"]:
                if section.get("TOCHeading") == "Names and Identifiers":
                    if "Section" in section:
                        for sub_section in section["Section"]:
                            if sub_section.get("TOCHeading") == "CAS Registry Number":
                                if "Information" in sub_section:
                                    for info in sub_section["Information"]:
                                        if info.get("Name") == "CAS_NUMBER" and "StringValue" in info:
                                            cas_number = info["StringValue"]
                                            break
                            if sub_section.get("TOCHeading") in ["Other Identifiers", "Depositor-Supplied Synonyms",
                                                                 "Substance Names"]:
                                if "Information" in sub_section:
                                    for info in sub_section["Information"]:
                                        if info.get(
                                                "Name") == "External Identifier" and "Value" in info and "StringWithMarkup" in \
                                                info["Value"]:
                                            for item in info["Value"]["StringWithMarkup"]:
                                                s = item["String"]
                                                if "INN:" in s.upper() or "(INN)" in s.upper() or "international nonproprietary name" in s.lower():
                                                    match = re.search(
                                                        r'(INN:\s*([A-Za-z0-9\s,\-]+))|(([A-Za-z0-9\s,\-]+)\s*\(INN\))',
                                                        s, re.IGNORECASE)
                                                    if match:
                                                        inn_value = match.group(2) or match.group(4)
                                                        if inn_value:
                                                            inn = inn_value.strip()
                                                            break
                                            if inn:
                                                break
                                if inn:
                                    break
                        if cas_number and inn:
                            break

    return inn, cas_number, english_name


# --- 从分类路径中提取 Disease 和 Target ---
def extract_disease_target(classification_path):
    """
    根据分类路径提取 Disease 和 Target。
    假设：
    - 如果路径以 "Drugs" 开头，且长度足够，则将第三个元素作为 Disease，第四个元素作为 Target。
    - 否则，将第二个元素作为 Disease，第三个元素作为 Target。
    """
    disease = None
    target = None

    if classification_path and classification_path[0] == "Drugs":
        if len(classification_path) > 2:
            disease = classification_path[2]
        if len(classification_path) > 3:
            target = classification_path[3]
    else:
        if len(classification_path) > 1:
            disease = classification_path[1]
        if len(classification_path) > 2:
            target = classification_path[2]

    return disease, target


# --- 主遍历函数 ---
def traverse_classification(node_id=None, current_path=None):
    """
    递归遍历 PubChem 分类树。
    从叶子节点提取药物信息，打印到终端，并追加写入药品目录文件。
    """
    global is_first_entry  # 声明使用全局变量

    if current_path is None:
        current_path = []

    if node_id in processed_nodes:
        return
    processed_nodes.add(node_id)

    base_url = "https://pubchem.ncbi.nlm.nih.gov/classification_2/classification_2.fcgi"
    params = {
        "hid": 96,
        "depth": 1,
        "format": "json"
    }
    if node_id and node_id != "root":
        params["start"] = node_id

    try:
        response = requests.get(base_url, params=params,
                                timeout=REQUEST_TIMEOUT_SECONDS_CLASSIFICATION)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"错误: 请求分类数据失败 (NodeID: {node_id}): {e}")
        return
    finally:
        time.sleep(API_REQUEST_DELAY_SECONDS)

    nodes_in_response = []
    if "Hierarchies" in data and "Hierarchy" in data["Hierarchies"] and data["Hierarchies"]["Hierarchy"]:
        if "Node" in data["Hierarchies"]["Hierarchy"][0]:
            nodes_in_response = data["Hierarchies"]["Hierarchy"][0]["Node"]

    actual_child_nodes = []
    if node_id is None or node_id == "root":
        actual_child_nodes = nodes_in_response
    else:
        for node in nodes_in_response:
            if node_id in node.get("ParentID", []):
                actual_child_nodes.append(node)

    for node in actual_child_nodes:
        node_description = node["Information"]["Description"]["StringWithMarkup"][0]["String"]
        current_processing_node_id = node["NodeID"]

        new_path = current_path + [node_description]

        if current_processing_node_id in processed_nodes:
            continue

        if "ChildID" not in node["Information"] or not node["Information"]["ChildID"]:
            print(f"\n--- 检测到叶子节点: {node_description} (NodeID: {current_processing_node_id}) ---")
            pubchem_cid = get_pubchem_cid(node_description)

            if pubchem_cid:
                raw_pubchem_json = get_pubchem_compound_raw_json(pubchem_cid)
                if raw_pubchem_json:
                    # 提取 INN, CAS 和 PubChem 英文名
                    inn, cas_number, english_name_from_pubchem = extract_inn_cas_and_english_name(raw_pubchem_json)

                    final_drug_english_name = english_name_from_pubchem if english_name_from_pubchem else node_description

                    # 提取 disease 和 target
                    disease, target = extract_disease_target(new_path[:-1])

                    # 构建要保存的药品目录条目
                    drug_catalog_entry = {
                        "classification_path": new_path[:-1],
                        "disease": disease,
                        "target": target,
                        "drug_name": node_description,
                        "english_name_from_pubchem": final_drug_english_name,
                        "pubchem_cid": pubchem_cid,
                        "inn": inn,
                        "cas_number": cas_number
                    }

                    # **打印要保存的字段到终端**
                    print("准备写入目录文件的药品信息:")
                    print(json.dumps(drug_catalog_entry, ensure_ascii=False, indent=2))
                    print("--- 目录信息打印结束 ---")

                    # **追加写入到药品目录文件**
                    try:
                        with open(DRUG_CATALOG_FILENAME, "a", encoding="utf-8") as f:
                            if not is_first_entry:
                                f.write(",\n")  # 非第一个条目，前面加逗号换行
                            json.dump(drug_catalog_entry, f, ensure_ascii=False, indent=4)
                            is_first_entry = False  # 标记已写入第一个条目
                        print(f"成功追加写入到 '{DRUG_CATALOG_FILENAME}'。")
                    except IOError as e:
                        print(f"错误: 无法追加写入药品目录信息到文件 '{DRUG_CATALOG_FILENAME}': {e}")
                    except Exception as e:
                        print(f"错误: 追加写入药品目录信息时发生意外错误: {e}")

                else:
                    print(f"警告: 未能获取 '{node_description}' (CID: {pubchem_cid}) 的原始详细信息 (PUG-View)。")
            else:
                print(f"警告: 未能获取 '{node_description}' 的 PubChem CID。")
        else:
            print(f"进入分类: {node_description} (NodeID: {current_processing_node_id})")
            traverse_classification(current_processing_node_id, new_path)

        processed_nodes.add(current_processing_node_id)


# --- 主执行块 ---
if __name__ == "__main__":
    print("PubChem 药物分类数据爬虫开始运行（药品目录信息将打印到终端并追加写入文件）...")

    # 确保药品目录文件的父目录存在
    catalog_dir = os.path.dirname(DRUG_CATALOG_FILENAME)
    if catalog_dir and not os.path.exists(catalog_dir):
        try:
            os.makedirs(catalog_dir, exist_ok=True)
            print(f"创建药品目录文件路径: {catalog_dir}")
        except Exception as e:
            print(f"错误: 无法创建药品目录的目标路径 '{catalog_dir}': {e}")
            print("请检查路径是否存在或权限是否足够。程序将退出。")
            exit()  # 如果无法创建目录，则无法写入文件，直接退出

    # 初始化/清空药品目录文件并写入 JSON 数组的开头
    try:
        with open(DRUG_CATALOG_FILENAME, "w", encoding="utf-8") as f:
            f.write("[\n")  # 写入 JSON 数组的起始符
        print(f"已创建或清空 '{DRUG_CATALOG_FILENAME}' 文件，准备追加写入。")
    except IOError as e:
        print(f"错误: 无法创建/清空文件 '{DRUG_CATALOG_FILENAME}': {e}")
        print("请检查文件路径或权限。程序将退出。")
        exit()

    # 从分类树的根部开始遍历，启动爬虫。
    traverse_classification(node_id="root", current_path=[])

    # 爬取完成后，追加写入 JSON 数组的结尾
    try:
        with open(DRUG_CATALOG_FILENAME, "a", encoding="utf-8") as f:
            f.write("\n]\n")  # 写入 JSON 数组的结束符
        print(f"\n爬取过程完成。所有药品的目录信息已保存到 '{DRUG_CATALOG_FILENAME}'。")
    except IOError as e:
        print(f"错误: 无法完成写入药品目录文件 '{DRUG_CATALOG_FILENAME}': {e}")
    except Exception as e:
        print(f"错误: 完成写入药品目录时发生意外错误: {e}")