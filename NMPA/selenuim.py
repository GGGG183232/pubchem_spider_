from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

# 随机生成一个user-agent
def get_random_user():
    # userAgent可用列表
    user_list = [
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',

        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',

        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',

        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 2.0.50727; SLCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; Tablet PC 2.0; .NET4.0E)',

        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB7.0)',

        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201',

        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',

        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E) QQBrowser/6.9.11079.201',
        ]
    return random.choice(user_list)
    pass


def search_nmpa_drug():
    """
    使用 Selenium 访问国家药品监督管理局（NMPA）的网站，
    输入药品名称“阿司匹林”，并点击搜索按钮。
    """
    # ------------------ 设置 Chrome 浏览器选项 ------------------
    chrome_options = Options()

    # 启用无头模式
    # "--headless=new" 是较新的语法，更推荐使用
    # chrome_options.add_argument("--headless=new")

    # 如果需要，你也可以添加其他参数，例如禁用GPU加速以提高稳定性
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # 在无头模式下，`detach` 选项将不起作用，因为没有UI可以保持
    chrome_options.add_experimental_option("detach", True)

    # ------------------ 初始化 WebDriver ------------------
    # 如果已将 ChromeDriver 路径添加到系统环境变量，可以这样初始化
    # 设置浏览器



    options = webdriver.ChromeOptions()
    # 修改window.navigator.webdriver为undefined，防机器人识别机制，selenium自动登陆判别机制
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument("--disable-blink-features=AutomationControlled")
    # 更换头部
    a_user = get_random_user()  # 自定义函数用来更改user-agent,避免爬虫被识别
    options.add_argument('user-agent=' + a_user)
    driver = webdriver.Chrome(options=options)

    # driver = webdriver.Chrome(options=chrome_options)
    # driver.
    # 如果没有，请使用 Service 对象
    # service = Service('your_chromedriver_path_here')
    # driver = webdriver.Chrome(service=service, options=chrome_options)

    # ------------------ 访问指定 URL ------------------
    url = "https://www.nmpa.gov.cn/datasearch/home-index.html#category=yp"
    print(f"正在访问：{url}")
    driver.get(url)
    # 设置浏览器


    # print(driver.page_source)

    # ------------------ 等待页面加载 ------------------
    # 使用 WebDriverWait 等待搜索输入框出现，这比 time.sleep() 更可靠
    try:
        wait = WebDriverWait(driver, 10)

        print("关闭键")
        close_button = driver.find_element(By.CLASS_NAME, 'introjs-skipbutton')
        print("关闭")
        close_button.click()
        # 找到输入框并输入药品名称
        search_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="请输入批准文号"]')))
        print("找到搜索输入框，正在输入“阿司匹林”...")
        search_input.send_keys("阿司匹林")

        # 找到并点击搜索按钮
        print("点击确认")
        # 找到i标签，它具有类名'el-icon-search'
        search_icon = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "i.el-icon-search")))
        print("找到搜索图标...")
        search_icon.click()

        print("搜索已完成。")

        # 等待搜索结果页面加载
        time.sleep(5)
        print("搜索结果页面标题是：", driver.title)

        close_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.introjs-button.introjs-skipbutton"))
        )
        print(driver.page_source)
        close_btn.click()
        print("关闭按钮已点击")
        print("成功点击关闭按钮。")
    except Exception as e:
        print(f"发生错误：{e}")
        # 如果出错，也可以选择关闭浏览器
        # driver.quit()


# 调用函数
if __name__ == "__main__":
    search_nmpa_drug()
