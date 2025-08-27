import pandas as pd
import requests
import time
import os

# --- 1. 基本配置 ---

# POST请求的目标URL
SEARCH_URL = "https://www.drugfuture.com/synth/Search.aspx"
# GET请求的来源页/检索页URL，我们从这里获取初始Cookie
SEARCH_PAGE_URL = "https://www.drugfuture.com/synth/synth_query.asp"

# 请求头 (User-Agent是必须的，Referer也很重要)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0',
    'Referer': SEARCH_PAGE_URL,  # 告诉服务器我们是从搜索页面提交的请求
    'Origin': 'https://www.drugfuture.com',
    'Content-Type': 'application/x-www-form-urlencoded',
}


# --- 2. 核心爬取函数 ---

def search_drug_robust(drug_name, session):
    """
    一个更健壮的查询函数，它先访问搜索页获取cookie，然后再提交POST请求。

    Args:
        drug_name (str): 要查询的药品名称.
        session (requests.Session): requests的会话对象.

    Returns:
        str: 成功时返回HTML文本，失败时返回None.
    """
    print(f"正在查询: {drug_name}...")

    try:
        # 第一步：先用GET请求访问搜索页面。
        # Session对象会自动保存服务器返回的任何Cookie。
        # 这一步是关键！
        session.get(SEARCH_PAGE_URL, headers=HEADERS, timeout=15)
        print(" -> 已访问搜索页，获取初始Cookie。")

        # 构造POST表单数据
        form_data = {
            'DRUG_NAME': drug_name,
            'CHEMICAL_NAME': '',
            'CAS_NUMBER': '',
        }

        # 第二步：使用同一个session对象发送POST请求。
        # Session会自动附上刚才从GET请求中收到的Cookie。
        response = session.post(SEARCH_URL, headers=HEADERS, data=form_data, timeout=15)

        response.raise_for_status()
        response.encoding = response.apparent_encoding

        print(f" -> 查询成功: {drug_name}")
        return response.text

    except requests.exceptions.RequestException as e:
        print(f"查询失败: {drug_name}, 错误: {e}")
        return None


# --- 3. 主逻辑 (与之前相同) ---

if __name__ == "__main__":
    csv_file_path = r"E:\PROJECT\25_71_Robinagent\spider\drugfuture\chemical_substances.csv"
    output_dir = r"E:\PROJECT\25_71_Robinagent\drugfuture_html"
    os.makedirs(output_dir, exist_ok=True)

    try:
        df = pd.read_csv(csv_file_path)
        drug_names = df['name'].dropna().tolist()
        print(f"从CSV文件中成功读取 {len(drug_names)} 个药品名称。")
    except Exception as e:
        print(f"读取CSV文件时出错: {e}")
        exit()

    # 创建一个Session对象，后续的所有操作都通过它进行
    with requests.Session() as session:
        for name in drug_names:
            # 注意，我们现在调用的是新的、更健壮的函数
            html_content = search_drug_robust(name, session)

            if html_content:
                safe_filename = "".join(c for c in name if c.isalnum() or c in (' ', '_')).rstrip()
                file_path = os.path.join(output_dir, f"{safe_filename}.html")

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f" -> 结果已保存至: {file_path}")

            print("--- 等待2秒 ---")
            time.sleep(2)

    print(f"\n所有查询任务已完成！文件已全部下载到 {output_dir}")