import requests
import json
import csv
import pandas as pd
import time
import random
import os

# 定义要读取的CSV文件路径和要写入的CSV文件路径
INPUT_CSV_PATH = r"E:\PROJECT\25_71_Robinagent\spider\part_1.csv"
OUTPUT_CSV_PATH = r"E:\PROJECT\25_71_Robinagent\spider\synthesis_routes.csv"


# 定义爬虫核心函数
def fetch_synthesis_routes(cas_id):
    """
    根据CAS号爬取化源网的合成路线信息。
    """
    print(f"--- 开始爬取 CAS号: {cas_id} 的合成路线 ---")
    all_routes = []
    start_index = 0
    # 每次请求3条数据，实际值可以根据观察调整
    perHcRow = 100

    while True:
        end_index = start_index + perHcRow

        payload = {
            'act': 'GetHeCenData',
            'casId': cas_id,
            'start': start_index,
            'end': end_index
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }

        try:
            # 增加随机延迟，避免被服务器封禁
            time.sleep(random.uniform(1, 3))

            response = requests.post("https://www.chemsrc.com/SearchSup", data=payload, headers=headers, timeout=10)
            response.raise_for_status()

            json_data = response.json()
            synthesis_routes = json_data.get('data', [])

            # 如果没有返回数据，说明已经爬取完毕
            if not synthesis_routes:
                print(f"CAS号: {cas_id} 的合成路线已全部爬取完毕。")
                break

            all_routes.extend(synthesis_routes)
            print(f"  - 成功获取索引 {start_index} 到 {end_index} 的数据。")

            # 更新下一页的起始索引
            start_index = end_index

        except requests.exceptions.RequestException as e:
            print(f"  - 请求失败，CAS号: {cas_id}, 错误: {e}")
            break

    return all_routes


# 定义写入CSV文件的函数
def append_to_csv(cas_id, routes_data, output_path):
    """
    将合成路线数据追加写入到CSV文件中。
    """
    # 检查文件是否存在，如果不存在则写入表头
    file_exists = os.path.exists(output_path)

    with open(output_path, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['CAS', 'refid', 'ref', 'hcdat_raw']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for route in routes_data:
            # 将复杂的hcdat字段序列化为JSON字符串以便保存
            hcdat_str = json.dumps(route.get('hcdat', []), ensure_ascii=False)

            row = {
                'CAS': cas_id,
                'refid': route.get('refid'),
                'ref': route.get('ref'),
                'hcdat_raw': hcdat_str
            }
            writer.writerow(row)
    print(f"--- CAS号: {cas_id} 的数据已成功追加写入到 {output_path} ---")


# 主函数
def main():
    """
    主程序，负责协调读取、爬取和写入操作。
    """

    # 使用pandas读取CSV文件，确保数据准确性
    df = pd.read_csv(INPUT_CSV_PATH, encoding='GB18030')

    # 确保CSV文件中包含'CAS'字段
    if 'cas_number' not in df.columns:
        print(f"错误：输入文件 {INPUT_CSV_PATH} 中没有名为 'cas_number' 的列。")
        return

    cas_numbers = df['cas_number'].dropna().unique()

    print(f"成功读取 {len(cas_numbers)} 个唯一的CAS号。")

    for cas_number in cas_numbers:
        # 爬取当前CAS号的所有合成路线
        routes = fetch_synthesis_routes(str(cas_number).strip())

        if routes:
            # 将爬取到的数据追加写入CSV文件
            append_to_csv(str(cas_number).strip(), routes, OUTPUT_CSV_PATH)
        else:
            print(f"CAS号: {cas_number} 未找到合成路线。")




if __name__ == "__main__":
    main()