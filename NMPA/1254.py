from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


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
    driver = webdriver.Chrome(options=chrome_options)
    # driver.
    # 如果没有，请使用 Service 对象
    # service = Service('your_chromedriver_path_here')
    # driver = webdriver.Chrome(service=service, options=chrome_options)

    # ------------------ 访问指定 URL ------------------
    url = "https://www.nmpa.gov.cn/datasearch/home-index.html#category=yp"
    print(f"正在访问：{url}")
    driver.get(url)