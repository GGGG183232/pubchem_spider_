import json
import csv
import os


def parse_smiles_from_json(json_file_path, json_path_list):
    """
    从一个 JSON 文件中解析出 SMILES 字符串。

    参数:
    json_file_path (str): JSON 文件的完整路径。
    json_path_list (list): 一个列表，表示从 JSON 根目录到 SMILES 值的键或索引路径。
                          例如: ['Record', 'Section', 2, 'Section', 1, 'Section', 3, 'Information', 0, 'Value']

    返回:
    str: 解析出的 SMILES 字符串，如果找不到则返回 None。
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 沿着路径导航到 SMILES 值
        current_data = data
        for key in json_path_list:
            if isinstance(current_data, dict) and key in current_data:
                current_data = current_data[key]
            elif isinstance(current_data, list) and isinstance(key, int) and 0 <= key < len(current_data):
                current_data = current_data[key]
            else:
                print(
                    f"警告: 无法在文件 '{json_file_path}' 的路径 '{' -> '.join(map(str, json_path_list))}' 找到 SMILES。路径在 '{key}' 处中断。")
                return None

        return str(current_data)

    except FileNotFoundError:
        print(f"错误: 找不到文件 {json_file_path}")
        return None
    except json.JSONDecodeError:
        print(f"错误: 无法解析 JSON 文件 {json_file_path}")
        return None
    except Exception as e:
        print(f"解析文件 '{json_file_path}' 过程中发生错误: {e}")
        return None


def append_to_csv(csv_file_path, smiles_string, header=['SMILES']):
    """
    将 SMILES 字符串追加写入到 CSV 文件的末尾。

    参数:
    csv_file_path (str): CSV 文件的完整路径。
    smiles_string (str): 要写入的 SMILES 字符串。
    header (list): CSV 文件的列标题。如果文件不存在，将创建并写入此标题。
    """
    if not smiles_string:
        print("没有 SMILES 字符串可写入，跳过。")
        return

    # 检查 CSV 文件是否存在，如果不存在则创建并写入标题
    file_exists = os.path.exists(csv_file_path)

    # 确保 CSV 文件所在的目录存在
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

    with open(csv_file_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        if not file_exists or os.stat(csv_file_path).st_size == 0:
            writer.writerow(header)

        writer.writerow([smiles_string])
        print(f"成功将 SMILES '{smiles_string}' 写入到 {csv_file_path}")


# --- 主程序部分 ---
if __name__ == "__main__":
    # 1. 设置文件路径
    # 使用你提供的具体路径
    json_file_path_example = r"E:\PROJECT\25_71_Robinagent\spider\pubchem_drugs_raw_json\1046_Pyrazinamide.json"

    # 设置 CSV 文件的保存路径，可以自定义
    csv_file_path_example = r"E:\PROJECT\25_71_Robinagent\spider\extracted_smiles.csv"

    # 2. 定义从 JSON 根目录到 SMILES 值的路径
    # 假设这个路径对于所有 JSON 文件都是一样的
    CAS_path = ['Record', 'Section', 2, 'Section', 3, 'Section', 0, 'Information']
    Melting_point_path = ['Record', 'Section', 3, 'Section', 1, 'Section', 3, 'Information', 3, 'Value']
    Boiling_point_path = ['Record', 'Section', 3, 'Section', 1, 'Section', 2, 'Information', 0, 'Value']
    Solubility_path = ['Record', 'Section', 3, 'Section', 1, 'Section', 4, 'Information', 5, 'Value']
    logP_path = ['Record', 'Section', 3, 'Section', 1, 'Section', 5, 'Information', 2, 'Value']
    pKa_path = ['Record', 'Section', 3, 'Section', 1, 'Section', 9, 'Information', 0, 'Value']
    RotatableBondCount_path = ['Record', 'Section', 3, 'Section', 0, 'Section', 4, 'Information', 0, 'Value']
    HydrogenBondAcceptorCount_path = ['Record', 'Section', 3, 'Section', 0, 'Section', 3, 'Information', 0, 'Value']
    HydrogenBondDonorCount_path = ['Record', 'Section', 3, 'Section', 0, 'Section', 2, 'Information', 0, 'Value']
    HeavyAtomCount_path = ['Record', 'Section', 3, 'Section', 0, 'Section', 8, 'Information', 0, 'Value']
    TopologicalPolarSurfaceArea_path = ['Record', 'Section', 3, 'Section', 0, 'Section', 7, 'Information', 0, 'Value']

    # EINECS_path = ['Record', 'Section', 2, 'Section', 4, 'Section', 1, 'Information', 1, 'Value', 'StringWithMarkup']
    # 3. 解析 SMILES 字符串
    CAS = parse_smiles_from_json(json_file_path_example, CAS_path)
    Melting_point = parse_smiles_from_json(json_file_path_example, Melting_point_path)
    Boiling_point = parse_smiles_from_json(json_file_path_example, Boiling_point_path)
    Solubility = parse_smiles_from_json(json_file_path_example, Solubility_path)
    logP = parse_smiles_from_json(json_file_path_example, logP_path)
    pKa = parse_smiles_from_json(json_file_path_example, pKa_path)
    RotatableBondCount = parse_smiles_from_json(json_file_path_example, RotatableBondCount_path)
    # EINECS = parse_smiles_from_json(json_file_path_example, EINECS_path)
    HydrogenBondAcceptorCount = parse_smiles_from_json(json_file_path_example, HydrogenBondAcceptorCount_path)
    HydrogenBondDonorCount = parse_smiles_from_json(json_file_path_example, HydrogenBondDonorCount_path)
    HeavyAtomCount = parse_smiles_from_json(json_file_path_example, HeavyAtomCount_path)
    TopologicalPolarSurfaceArea = parse_smiles_from_json(json_file_path_example, TopologicalPolarSurfaceArea_path)

    row = []
    row.append(CAS,Melting_point)


    # 4. 将 SMILES 字符串追加写入 CSV 文件

    if smiles:
        append_to_csv(csv_file_path_example, smiles)
