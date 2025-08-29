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