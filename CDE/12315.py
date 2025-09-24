import requests
import json


def debug_single_drug(target_detail_url):
    """
    这是一个用于调试的函数，用于抓取单个药品详情页的数据。
    它会打印出每一步的操作和结果，帮助理解反爬虫规避的流程。
    """
    print("--- 开始调试程序 ---")

    # 1. [伪装] 准备通用的浏览器请求头 (User-Agent)
    #    这是反爬第一步：告诉服务器我们是“普通浏览器”
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    }
    print(f"步骤 1: 已设置 User-Agent -> {headers['User-Agent'][:50]}...")

    # 2. [会话] 创建一个 Session 对象
    #    Session 会像浏览器一样自动管理 Cookies
    session = requests.Session()
    print("步骤 2: 已创建 requests.Session() 对象")

    # 3. [获取Cookie] 访问网站首页 "预热" Session
    #    这是关键一步，让 Session 获取初始的合法 Cookie
    main_url = "https://www.cde.org.cn/"
    try:
        session.get(main_url, headers=headers, timeout=10)
        print(f"步骤 3: 成功访问首页 '{main_url}'，获取初始 Cookie")
        # 我们可以查看一下session里现在有什么cookie
        # print(" > 当前 Session 中的 Cookies:", session.cookies.get_dict())
    except requests.RequestException as e:
        print(f"错误: 访问首页失败，请检查网络连接。 {e}")
        return

    # 4. [提取ID] 从目标详情页URL中提取关键ID
    #    这是向API发送请求所需的核心参数
    try:
        id_code = target_detail_url.split('/')[-1]
        print(f"步骤 4: 从URL '{target_detail_url}' 中提取到 ID -> {id_code}")
    except IndexError:
        print("错误: 无法从URL中提取ID，请检查URL格式。")
        return

    # 5. [准备请求] 准备发送到真正数据接口 (API) 的请求
    api_url = "https://www.cde.org.cn/hymlj/getInfoById"
    # 准备要 POST 的数据
    payload = {"idCode": id_code}

    # 准备这次API请求专用的请求头，特别是 Referer
    api_headers = headers.copy()
    api_headers["Content-Type"] = "application/x-www-form-urlencoded"
    # [伪装来源] 设置 Referer，告诉服务器我们是从哪个页面来的
    api_headers["Referer"] = target_detail_url
    print("步骤 5: 准备向 API 发送 POST 请求")
    print(f" > API URL: {api_url}")
    print(f" > 发送的数据 (Payload): {payload}")
    print(f" > Referer 请求头: {api_headers['Referer']}")

    # 6. [发送请求] 执行 POST 请求，获取最终数据
    print("\n--- 正在发送最终请求，请稍候... ---\n")
    try:
        response = session.post(api_url, data=payload, headers=api_headers, timeout=10)

        print(f"步骤 6: 收到服务器响应，状态码: {response.status_code}")

        # 7. [处理结果] 解析服务器返回的数据
        if response.status_code == 200:
            try:
                # 尝试将返回结果解析为 JSON
                result_data = response.json()
                print("步骤 7: 成功解析响应为 JSON 格式，数据如下:")

                # 使用 json.dumps 美化输出，方便查看
                pretty_json = json.dumps(result_data, indent=4, ensure_ascii=False)
                print(pretty_json)

            except json.JSONDecodeError:
                print("错误: 响应不是有效的 JSON 格式。")
                print("服务器返回的原始文本内容:", response.text)
        else:
            print(f"错误: 请求失败，状态码为 {response.status_code}")
            print("服务器返回内容:", response.text)

    except requests.RequestException as e:
        print(f"错误: API 请求失败。 {e}")

    print("\n--- 调试程序结束 ---")


if __name__ == "__main__":
    # --- 你可以在这里修改成任何你想调试的药品详情页链接 ---
    # 这是一个示例URL，来自CDE网站的“突破性治疗品种”公示列表
    example_url = "https://www.cde.org.cn/main/xxgk/listpage/4b525ac984cd5abe0b62174c88383a15"

    debug_single_drug(example_url)