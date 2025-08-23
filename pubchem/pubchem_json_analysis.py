import json
import csv
import os

# ========================= 配置 =========================
target_fields = [
    "CAS",
    "PubChem CID",
    "Molecular Formula",
    "Synonyms",
    "Molecular Weight",
    "Description",
    "InChI",
    "InChIKey",
    "SMILES",
    "European Community (EC) Number",
    "ChEBI ID",
    "Color / Form",
    "Drug Indication",
    "Drug Classes",
    "Clinical Trials",
    "Therapeutic area",
    "INN/Common name",
    "Melting point",
    "Boiling point",
    "Flash Point",
    "Density",
    "Solubility",
    "Odor",
    "Color3/Form",
    "logP",
    "pKa",
    "Rotatable Bond Count",
    "Hydrogen Bond Acceptor Count",
    "Hydrogen Bond Donor Count",
    "Heavy Atom Count",
    "Topological Polar Surface Area"
]
input_folder = r"E:\PROJECT\25_71_Robinagent\pubchem_drugs_raw_json"
output_csv = r"E:\PROJECT\25_71_Robinagent\spider\pubchem\7.1理化性质表.csv"
paths_file = r"E:\PROJECT\25_71_Robinagent\spider\pubchem\field_paths.json"  # 保存字段路径

# ========================= 工具函数 =========================
def load_paths():
    if os.path.exists(paths_file):
        with open(paths_file, "r", encoding="utf-8") as f:
            return json.load(f)     # 将json转化为python字典
    return {}

def save_paths(paths):
    with open(paths_file, "w", encoding="utf-8") as f:
        json.dump(paths, f, ensure_ascii=False, indent=2)

# def parse_value_from_json(json_file_path, json_paths_list):
#     """根据路径列表依次尝试提取值"""
#     try:
#         with open(json_file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)     # 把药物json转为字典
#
#         for path in json_paths_list:    # 给出字段路径列表，有多条路径逐个遍历
#             current_data = data
#             found = True
#             for key in path:
#                 if isinstance(current_data, dict) and key in current_data:
#                     current_data = current_data[key]
#                 elif isinstance(current_data, list) and isinstance(key, int) and 0 <= key < len(current_data):
#                     current_data = current_data[key]
#                 else:
#                     found = False
#                     break
#             if found:
#                 return current_data
#         return None
#     except Exception as e:
#         print(f"[错误] {json_file_path} 解析失败: {e}")
#         return None

import json
import os


def parse_value_from_json(json_file_path, json_paths_list, field):
    """
    根据成对的路径列表依次尝试提取值。
    - 首先，根据原始路径检查字段名是否匹配。
    - 如果匹配，则根据对应的值路径提取数据。
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 遍历成对的路径，例如 [["path1"], ["value_path1"]]
        for original_path, value_path in json_paths_list:

            # --- 步骤 1: 验证原始路径的字段名 ---
            original_value = data
            found_original = True
            for key in original_path:
                if isinstance(original_value, dict) and key in original_value:
                    original_value = original_value[key]
                elif isinstance(original_value, list) and isinstance(key, int) and 0 <= key < len(original_value):
                    original_value = original_value[key]
                else:
                    found_original = False
                    break

            # 检查原始路径是否找到值，并且该值是否与目标字段名匹配（忽略大小写）
            if found_original and isinstance(original_value, str) and original_value.lower() == field.lower():

                # --- 步骤 2: 提取值路径的数据 ---
                final_value = data
                found_final = True
                for key in value_path:
                    if isinstance(final_value, dict) and key in final_value:
                        final_value = final_value[key]
                    elif isinstance(final_value, list) and isinstance(key, int) and 0 <= key < len(final_value):
                        final_value = final_value[key]
                    else:
                        found_final = False
                        break

                # 如果成功提取到最终值，则返回
                if found_final:
                    return final_value

        # 如果所有路径都尝试了但未找到匹配的值
        return None

    except Exception as e:
        print(f"[错误] {json_file_path} 解析失败: {e}")
        return None


# def find_field_paths(json_data, target_fields):
#     """
#     增强版寻路：找到字段名路径后，继续向下寻找 "Value" 或 "StringWithMarkup"
#     返回：{字段名: [路径列表]}
#     """
#     lowercase_target_fields = {f.lower(): f for f in target_fields}
#     found_paths = {field: [] for field in target_fields}
#
#     def _traverse(data, current_path):
#         if all(found_paths[f] for f in target_fields):
#             return
#
#         if isinstance(data, str):
#             lower_data = data.lower()
#             if lower_data in lowercase_target_fields:
#                 original_field_name = lowercase_target_fields[lower_data]
#
#                 # 搜索父节点的 value 路径
#                 parent_path = current_path[:-1]
#                 parent_node = json_data
#                 for p in parent_path:
#                     parent_node = parent_node[p]
#
#                 value_paths = []
#
#                 def _find_value(node, path_prefix):
#                     if isinstance(node, dict):
#                         for k, v in node.items():
#                             new_path = path_prefix + [k]
#                             if k in ("String", "Number"):
#                                 value_paths.append(new_path)
#                             _find_value(v, new_path)
#                     elif isinstance(node, list):
#                         for idx, item in enumerate(node):
#                             _find_value(item, path_prefix + [idx])
#
#                 _find_value(parent_node, parent_path)
#
#                 if value_paths:
#                     for vp in value_paths:
#                         if vp not in found_paths[original_field_name]:
#                             found_paths[original_field_name].append(vp)
#                 else:
#                     # 如果没找到 value，存字段路径
#                     if current_path not in found_paths[original_field_name]:
#                         found_paths[original_field_name].append(current_path)
#             return
#
#         if isinstance(data, dict):
#             for k, v in data.items():       # .item()把字典处理成元组，然后遍历元组
#                 _traverse(v, current_path + [k])
#         elif isinstance(data, list):
#             for idx, item in enumerate(data):
#                 _traverse(item, current_path + [idx])
#
#     _traverse(json_data, [])
#     return found_paths


def find_field_paths(json_data, target_fields):
    """
    增强版寻路：找到字段名路径后，将其原始路径和值路径配对存储。
    返回：{字段名: [[原始路径, 值路径], [原始路径, 值路径], ...]}
    """
    lowercase_target_fields = {f.lower(): f for f in target_fields}
    found_paths = {field: [] for field in target_fields}

    def _traverse(data, current_path):
        if all(found_paths[f] for f in target_fields):
            return

        if isinstance(data, str):
            lower_data = data.lower()
            if lower_data in lowercase_target_fields:
                original_field_name = lowercase_target_fields[lower_data]

                # 检查是否已找到这个原始路径，避免重复处理
                is_path_found = any(current_path == pair[0] for pair in found_paths[original_field_name])
                if is_path_found:
                    return

                # 寻找父节点的具体值路径
                parent_path = current_path[:-1]
                parent_node = json_data
                try:
                    for p in parent_path:
                        parent_node = parent_node[p]
                except (KeyError, IndexError):
                    return

                value_paths = []

                def _find_value(node, path_prefix):
                    if isinstance(node, dict):
                        for k, v in node.items():
                            new_path = path_prefix + [k]
                            if k in ("String", "Number"):
                                value_paths.append(new_path)
                            _find_value(v, new_path)
                    elif isinstance(node, list):
                        for idx, item in enumerate(node):
                            _find_value(item, path_prefix + [idx])

                _find_value(parent_node, parent_path)

                # 将原始路径和所有找到的值路径配对存储
                if value_paths:
                    for vp in value_paths:
                        found_paths[original_field_name].append([current_path, vp])
                else:
                    # 如果没有找到值路径，则只存储原始路径
                    found_paths[original_field_name].append([current_path, []])

            return

        if isinstance(data, dict):
            for k, v in data.items():
                _traverse(v, current_path + [k])
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                _traverse(item, current_path + [idx])

    _traverse(json_data, [])
    return found_paths
# ========================= 主逻辑 =========================
def main():
    stored_paths = load_paths()     # 读取路径文件，返回字典（每个字段的路径）

    for field in target_fields:
        stored_paths.setdefault(field, [])      # 将字段路径文件没有的字段添加到字典中，对应的路径存为空
        # 相当于  字段路径字典.get()获取值，如果target_filed(目标字段列表)有但stored_paths没有，那么加入stored_paths中，并标记路径为空，方便后面添加。

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)    # 创建一个 CSV 写入器
        writer.writerow(["文件名"] + target_fields)    # 写入 CSV 文件的第一行，也就是文件头

        for filename in os.listdir(input_folder):
            if not filename.lower().endswith(".json"):      # 检查文件名是否以 .json 结尾（不区分大小写），如果不是，则跳过本次循环
                continue

            file_path = os.path.join(input_folder, filename)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)    # json.load:读成字典
            except Exception as e:
                print(f"[跳过] {filename} 读取失败: {e}")
                continue

            row = [filename]
            updated = False

            for field in target_fields:  # 逐个字段提取值
                value = None

                # 先尝试已有路径
                if stored_paths[field]:
                    value = parse_value_from_json(file_path, stored_paths[field], field)

                # 如果没取到，寻路补充
                if value is None:
                    new_paths = find_field_paths(json_data, [field])
                    if new_paths[field]:
                        for p in new_paths[field]:
                            if p not in stored_paths[field]:
                                stored_paths[field].append(p)
                                updated = True
                        value = parse_value_from_json(file_path, new_paths[field], field)

                row.append(value if value is not None else "")

            writer.writerow(row)

            if updated:
                save_paths(stored_paths)

            print(f"[完成] {filename} 解析完成")

if __name__ == "__main__":
    main()
