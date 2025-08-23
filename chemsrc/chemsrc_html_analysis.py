import os
import csv
import re
from bs4 import BeautifulSoup


def parse_computational_chemistry_data(html_content):
    """
    解析HTML内容，提取 <tr class="detail"> 中嵌套的计算化学键值对。

    Args:
        html_content (str): 包含计算化学数据的HTML字符串。

    Returns:
        dict: 包含解析后键值对的字典，如果解析失败则返回空字典。
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # 找到包含所有计算化学数据的 <td> 标签
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


def parse_html_file_and_append_to_csv(directory_path, output_csv_file):
    """
    遍历指定目录下的所有HTML文件，解析表格数据，并追加写入到CSV文件中。
    """
    # 检查输出CSV文件是否存在，如果不存在则创建并写入表头
    csv_exists = os.path.exists(output_csv_file)
    with open(output_csv_file, 'a', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        if not csv_exists:
            writer.writerow(['文件名', '键', '值'])

    # 遍历目录下的所有文件
    for filename in os.listdir(directory_path):
        if filename.endswith('.html'):
            file_path = os.path.join(directory_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()

                soup = BeautifulSoup(html_content, 'html.parser')
                rows = soup.find_all('tr', class_='detail')

                data_to_write = []
                # ① 解析普通 <tr class="detail"> 数据
                for row in rows:
                    key_element = row.find('th')
                    value_element = row.find('td')

                    if key_element and value_element:
                        key = key_element.get_text(strip=True)
                        value = value_element.get_text(strip=True)
                        if [filename, key, value] not in data_to_write:
                            data_to_write.append([filename, key, value])

                # ② 解析计算化学数据
                comp_chem_data = parse_computational_chemistry_data(html_content)
                for key, value in comp_chem_data.items():
                    if [filename, key, value] not in data_to_write:
                        data_to_write.append([filename, key, value])

                # ✅ 统一写入，避免重复
                if data_to_write:
                    with open(output_csv_file, 'a', newline='', encoding='utf-8-sig') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerows(data_to_write)
                    print(f"文件 '{filename}' 的数据已成功追加写入。")
                else:
                    print(f"文件 '{filename}' 中未找到可解析的数据。")

            except Exception as e:
                print(f"处理文件 '{filename}' 时发生错误: {e}")


# 定义你的文件路径
directory_path = r'E:\PROJECT\25_71_Robinagent\chemsrc_html'
output_csv_file = r'E:\PROJECT\25_71_Robinagent\spider\chemsrc\chemsrc_all_field.csv'  # 你要保存的CSV文件路径

# 调用函数开始批量处理
parse_html_file_and_append_to_csv(directory_path, output_csv_file)
