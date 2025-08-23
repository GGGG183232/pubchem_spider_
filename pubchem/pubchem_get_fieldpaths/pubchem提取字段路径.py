import json

# 你要找的字段英文名
target_fields = [
    "CAS",
    "Melting point",
    "Boiling point",
    "Flash Point",
    "Density",
    "Solubility",
    "Odor",
    "Color state",
    "logP",
    "pKa",
    "Rotatable Bond Count",
    "Hydrogen Bond Acceptor Count",
    "Hydrogen Bond Donor Count",
    "Heavy Atom Count",
    "Topological Polar Surface Area"
]  # 示例

# 文件路径
json_path = r"E:\PROJECT\25_71_Robinagent\spider\pubchem_drugs_raw_json\1046_Pyrazinamide.json"

# 读取 JSON
with open(json_path, "r", encoding="utf-8") as f:
    json_data = json.load(f)

# 存储结果
field_paths = {}     # {字段名: 字段路径}
value_values = {}    # {字段名: value值}
value_paths = {}     # {字段名: value路径}

# 大小写匹配映射
lowercase_target_fields = {f.lower() for f in target_fields}
field_mapping = {f.lower(): f for f in target_fields}

def _traverse(data, current_path):
    if len(field_paths) == len(target_fields):
        return

    if isinstance(data, str):
        lowercase_data = data.lower()
        if lowercase_data in lowercase_target_fields and field_mapping[lowercase_data] not in field_paths:
            original_field_name = field_mapping[lowercase_data]
            field_paths[original_field_name] = current_path

            # 找父节点
            if len(current_path) >= 1:
                parent_path = current_path[:-1]
                parent_node = json_data
                for p in parent_path:
                    parent_node = parent_node[p]

                # 搜索父节点中的 "Value" 字段
                def find_value_fields(node, path_prefix):
                    if isinstance(node, dict):
                        for k, v in node.items():
                            new_path = path_prefix + [k]
                            if k == "Value":
                                value_paths[original_field_name] = new_path
                                value_values[original_field_name] = v
                            find_value_fields(v, new_path)
                    elif isinstance(node, list):
                        for idx, item in enumerate(node):
                            find_value_fields(item, path_prefix + [idx])

                find_value_fields(parent_node, parent_path)
            return

    if isinstance(data, dict):
        for key, value in data.items():
            _traverse(value, current_path + [key])
    elif isinstance(data, list):
        for index, item in enumerate(data):
            _traverse(item, current_path + [index])

# 执行递归
_traverse(json_data, [])

# Step 1: 输出字段路径
print("=== 字段路径 ===")
for field in target_fields:
    if field in field_paths:
        print(f"{field}: {field_paths[field]}")

# Step 2: 输出字段 value 值
print("\n=== 字段 value 值 ===")
for field in target_fields:
    if field in value_values:
        print(f"{field}: {value_values[field]}")

# Step 3: 输出字段 value 的路径
print("\n=== 字段 value 路径 ===")
for field in target_fields:
    if field in value_paths:
        print(f"{field}: {value_paths[field]}")
