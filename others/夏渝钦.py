import time
import hashlib
import urllib.parse
from typing import Union, Dict, Any
import requests
from playwright.sync_api import sync_playwright
from requests import Request, Session

class WebScraper:
    def __init__(self):
        # 这里填你逆向出来的真实 app_secret（必须和前端一致）
        self.app_secret = "nmpasecret2020"

    def get_current_timestamp(self) -> int:
        """获取当前时间戳（毫秒）"""
        return int(time.time() * 1000)

    def params_str_sort(self, params_str: str) -> str:
        parts = params_str.split('&')
        parts.sort()
        return '&'.join(parts)

    def get_sign(self, params: Union[str, Dict[str, Any]]) -> str:
        if isinstance(params, str):
            return self.params_str_sort(params)
        elif isinstance(params, dict):
            param_pairs = []
            for key, value in params.items():
                if value not in ['', None, 'undefined']:
                    param_pairs.append(f"{key}={value}")
            param_str = '&'.join(param_pairs)
            return self.params_str_sort(param_str)
        return ""

    def json_md5_to_str(self, params: Union[str, Dict[str, Any]]) -> str:
        param_str = self.get_sign(params)
        signed_str = param_str + "&" + self.app_secret
        encoded_str = urllib.parse.quote(signed_str, safe='')
        replacements = {'!': '%21', '(': '%28', ')': '%29', '~': '%7E'}
        for char, replacement in replacements.items():
            encoded_str = encoded_str.replace(char, replacement)
        md5_hash = hashlib.md5(encoded_str.encode('utf-8')).hexdigest()
        return md5_hash


def get_cookies_and_headers():
    """用 Playwright 启动浏览器获取动态 Cookie"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # 建议调试时先开可视化
        page = browser.new_page()
        page.goto("https://www.nmpa.gov.cn/")
        page.wait_for_timeout(5000)

        # Playwright 获取上下文 cookie 列表
        cookies = page.context.cookies()

        # 转成 dict
        playwright_cookies = {c['name']: c['value'] for c in cookies}

        # 你需要的固定 cookie 名称顺序
        cookie_keys_order = [
            'STEP_TIPS_INDEX',
            'STEP_TIPS_RESULT',
            'arialoadData',
            'visualdevice',
            'ariawapChangeViewPort',
            'token',
            'NfBCSins2OywS',
            'ariauseGraymode',
            'ariaappid',
            'acw_tc',
            'NfBCSins2OywT'
        ]

        # 对应的默认值
        extra_defaults = {
            'STEP_TIPS_INDEX': 'true',
            'STEP_TIPS_RESULT': 'true',
            'arialoadData': 'true',
            'visualdevice': 'pc',
            'ariawapChangeViewPort': 'true',
            'token': '',
            'ariauseGraymode': 'false',
            'ariaappid': '84423173f7b7a6d06c86ce7c2d464036'
        }

        # 组装顺序 + 如果 Playwright 有值，就用 Playwright；没有就用 extra 默认；再没有就用空字符串
        ordered_cookie_pairs = []
        for key in cookie_keys_order:
            value = playwright_cookies.get(key) or extra_defaults.get(key) or ''
            ordered_cookie_pairs.append(f"{key}={value}")

        # 拼成最终字符串
        cookie_str = "; ".join(ordered_cookie_pairs)

        print("[按指定顺序组合的 Cookie] >>>", cookie_str)
        print(len(cookie_str))

        #browser.close()

        headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'https://www.nmpa.gov.cn/datasearch/search-info.html?nmpa=aWQ9NzZhZTYyOTA2M2MwZDYxY2Q3ZjNlMDAwYjZhNmMyNjEmaXRlbUlkPWZmODA4MDgxODNjYWQ3NTAwMTg0MDg4MWY4NDgxNzlm',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        #'sign': 'ab77f1d39e9221030bffd10ef9006cb6',
        #'timestamp': '1752336749000',
        'token': 'false',
        'Cookie': cookie_str
        }
        return headers

def query_detail():
    s = WebScraper()

    # ✅ 获取动态 Cookie 和标准请求头
    headers = get_cookies_and_headers()

    # ✅ 获取当前时间戳
    timestamp = s.get_current_timestamp()
    print("[当前时间戳] >>>", timestamp)

    # ✅ 设置请求参数
    params = {
        "itemId": "ff80808183cad75001840881f848179f",
        "id": "fefae409ec46517ef32f11a1c9b35226",
        "timestamp": timestamp
    }

    # ✅ 生成 sign（在此之前设置参数）
    sign = s.json_md5_to_str(params)
    print("[生成的 sign] >>>", sign)

    # ✅ 将生成的 sign 和 timestamp 加入到 headers 中
    headers["sign"] = sign
    headers["timestamp"] = str(timestamp)  # 如果有需要也可以动态拿

    # ✅ 参数准备
    params_ordered = [
        ("itemId", "ff80808183cad75001840881f848179f"),
        ("id", "fefae409ec46517ef32f11a1c9b35226"),
        ("timestamp", timestamp)
    ]

    # ✅ 请求 URL
    url = "https://www.nmpa.gov.cn/datasearch/data/nmpadata/queryDetail"

    # ✅ 使用 requests 库发起请求
    req = Request('GET', url, headers=headers, params=params_ordered)
    prepared = req.prepare()

    # 使用 Session 发送请求
    s = Session()
    resp = s.send(prepared)

    # ✅ 输出状态码和响应内容
    print("[状态码] >>>", resp.status_code)
    print("[响应内容] >>>", resp.text)


if __name__ == "__main__":
    query_detail()