import requests
# amoxicillin
# 搜索的目标 URL
url = "https://www.ema.europa.eu/en/search"

# --- 1. 定义查询参数 ---
# 这些是 URL 中 '?' 后面的部分
# requests 库会自动将它们格式化为正确的 URL 格式
params = {
    'search_api_fulltext': 'amoxicillin',
    'sort_bef_combine': 'search_api_relevance_DESC',
    # 使用 'f[]' 作为键，列表作为值，是 requests 库处理 f[0], f[1] 等参数的方式
    'f[]': 'ema_search_entity_is_document:Document',
    'form_url': ''  # 这个参数也存在于您的请求中
}

# --- 2. 定义请求头 (Headers) ---
# 这些请求头有助于模拟真实的网页浏览器，以确保服务器正确响应
# User-Agent (用户代理) 通常是最重要的一个
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    # 这个 User-Agent 与您提供的一致
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0'
}
# 注意: Cookie 和令牌 (如 'aws-waf-token') 通常是会话特定且会过期的。
# 最佳实践是让 `requests` 库自动管理会话，而不是硬编码这些值。
# 实践证明，即使没有它们，这个请求也能正常工作。


# --- 3. 发送 GET 请求 ---
try:
    print(f"🔍 正在发送请求，搜索关键词: '{params['search_api_fulltext']}'...")

    # 执行请求的核心命令
    response = requests.get(url, params=params, headers=headers)

    # 检查请求是否成功 (HTTP 状态码 200)
    response.raise_for_status()

    print(f"✅ 请求成功！收到服务器响应，状态码: {response.status_code}")

    # 查看实际请求的完整 URL
    print(f"实际请求的完整 URL: {response.url}\n")

    # --- 4. 处理响应内容 ---
    # response.text 中包含了页面的完整 HTML 内容
    # 我们打印前 1000 个字符作为预览
    print("--- 页面内容预览 (前 1000 个字符) ---")
    print(response.text[:1000])
    print("---------------------------------------")

    # 你可以像这样将完整内容保存到一个文件:
    # with open('ema_aspirin_search.html', 'w', encoding='utf-8') as f:
    #     f.write(response.text)
    # print("\n已将完整的 HTML 内容保存到 'ema_aspirin_search.html'")


except requests.exceptions.RequestException as e:
    print(f"❌ 发生错误: {e}")