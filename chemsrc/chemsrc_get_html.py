import os
import time
import pandas as pd
import requests

# 路径设置
csv_path = r"/spider/part_1.csv"
save_dir = r"/chemsrc_html"

# 创建保存文件夹
os.makedirs(save_dir, exist_ok=True)

# 请求头（模拟浏览器）
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Referer": "https://www.chemsrc.com/",
    "Accept-Language": "zh-CN,zh;q=0.9",
}
encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16', 'latin-1']
# 读取CSV
for encoding in encodings:
    try:
        df = pd.read_csv(csv_path, dtype=str, encoding=encoding)  # 保证CAS不会被当成数字处理
        cas_numbers = df["cas_number"].dropna().unique()
        break
    except UnicodeDecodeError:
        continue

print(f"共读取到 {len(cas_numbers)} 个 CAS 号")

# 循环爬取
for idx, cas in enumerate(cas_numbers, start=1):
    cas_clean = cas.strip()
    if not cas_clean:
        continue

    # 构造 URL（化源网 URL 后缀需要自己补 ID，这里先假设直接用 CAS）
    url = f"https://www.chemsrc.com/searchResult/{cas_clean}/"
    save_path = os.path.join(save_dir, f"{cas_clean}.html")

    # 如果已经存在则跳过
    if os.path.exists(save_path):
        print(f"[{idx}/{len(cas_numbers)}] {cas_clean} 已存在，跳过")
        continue

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            with open(save_path, "w", encoding=response.apparent_encoding) as f:
                f.write(response.text)
            print(f"[{idx}/{len(cas_numbers)}] {cas_clean} 保存成功")
        else:
            print(f"[{idx}/{len(cas_numbers)}] {cas_clean} 请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"[{idx}/{len(cas_numbers)}] {cas_clean} 请求出错: {e}")

    time.sleep(2)  # 防止被封，建议延迟

print("所有 CAS 号页面爬取完成！")
