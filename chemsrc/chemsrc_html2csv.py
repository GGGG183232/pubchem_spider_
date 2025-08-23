import os
import csv
import re
from bs4 import BeautifulSoup

# 定义你关心的特定字段
TARGET_FIELDS = [
    '熔点', '沸点', '闪点', '密度', '水溶解性', '外观性状', 'LogP',
    'PSA', '可旋转化学键数量', '氢键受体数量', '氢键供体数量', '重原子数量',
    '环数', '拓扑分子极性表面积（TPSA）'
]


def parse_computational_chemistry_data(html_content):
    """
    解析HTML内容，提取 <tr class="detail"> 中嵌套的计算化学键值对。
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    th_element = soup.find('th', string=re.compile("计算化学"))
    if not th_element:
        return {}

    td_element = th_element.find_next_sibling('td')
    if not td_element:
        return {}

    parsed_data = {}
    p_elements = td_element.find_all('p')
    for p_tag in p_elements:
        text = p_tag.get_text(strip=True)
        # 使用正则表达式匹配“键：值”的格式，并处理全角/半角冒号
        match = re.split(r'[:：]', text, 1)
        if len(match) == 2:
            key = match[0].strip()
            # 移除键开头的编号，例如 “1、”
            if re.match(r'^\d+、', key):
                key = re.sub(r'^\d+、', '', key).strip()
            value = match[1].strip()
            parsed_data[key] = value

    return parsed_data


def parse_html_file(file_path):
    """
    解析单个HTML文件，提取所有字段数据。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # 提取文件名作为药物ID
        drug_name = os.path.basename(file_path).replace('.html', '')
        drug_data = {'药物名称': drug_name}

        # ① 解析普通 <tr class="detail"> 数据
        rows = soup.find_all('tr', class_='detail')
        for row in rows:
            key_element = row.find('th')
            value_element = row.find('td')
            if key_element and value_element:
                key = key_element.get_text(strip=True)
                value = value_element.get_text(strip=True)
                if key not in drug_data:
                    drug_data[key] = value

        # ② 解析计算化学数据
        comp_chem_data = parse_computational_chemistry_data(html_content)
        for key, value in comp_chem_data.items():
            if key not in drug_data:
                drug_data[key] = value

        return drug_data

    except Exception as e:
        print(f"处理文件 '{file_path}' 时发生错误: {e}")
        return {}


def process_directory(directory_path, all_data_csv, target_data_csv):
    """
    遍历目录，解析所有HTML文件，并将数据写入两个CSV文件。
    """
    all_drugs_data = []

    # 遍历目录下的所有文件并解析
    for filename in os.listdir(directory_path):
        if filename.endswith('.html'):
            file_path = os.path.join(directory_path, filename)
            drug_data = parse_html_file(file_path)
            if drug_data:
                all_drugs_data.append(drug_data)
                print(f"文件 '{filename}' 解析完成。")

    if not all_drugs_data:
        print("未找到任何可解析的HTML文件。")
        return

    # --- 写入宽表CSV（所有字段） ---
    # 动态获取所有字段名
    all_headers = set()
    for drug in all_drugs_data:
        all_headers.update(drug.keys())

    # 将 set 转换为列表并排序，确保每次输出的列顺序一致
    all_headers = sorted(list(all_headers))

    with open(all_data_csv, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=all_headers)
        writer.writeheader()
        writer.writerows(all_drugs_data)
    print(f"\n所有数据已成功写入 '{all_data_csv}'。")

    # --- 写入窄表CSV（指定字段） ---
    # 确保目标字段都在数据中，并添加“药物名称”
    target_headers = ['药物名称'] + TARGET_FIELDS

    with open(target_data_csv, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=target_headers)
        writer.writeheader()

        for drug in all_drugs_data:
            # 创建一个只包含目标字段的新字典
            row = {header: drug.get(header, '') for header in target_headers}
            writer.writerow(row)
    print(f"指定字段数据已成功写入 '{target_data_csv}'。")


# 定义你的文件路径
directory_path = r'E:\PROJECT\25_71_Robinagent\chemsrc_html'
all_data_csv = r'E:\PROJECT\25_71_Robinagent\spider\chemsrc\all_drugs_data.csv'  # 所有字段的CSV文件
target_data_csv = r'E:\PROJECT\25_71_Robinagent\spider\chemsrc\target_drugs_data.csv'  # 指定字段的CSV文件

# 调用函数开始批量处理
process_directory(directory_path, all_data_csv, target_data_csv)