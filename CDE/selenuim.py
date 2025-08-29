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
    # driver = webdriver.Chrome(options=chrome_options)
    service = Service(r'C:\Users\26082\Downloads\edgedriver_win64\msedgedriver.exe')
    driver = webdriver.Edge(service=service)
    # driver.
    # 如果没有，请使用 Service 对象
    #
    # driver = webdriver.Chrome(service=service, options=chrome_options)

    # ------------------ 访问指定 URL ------------------
    url = "https://www.cde.org.cn/"
    print(f"正在访问：{url}")
    driver.get(url)

    # print(driver.page_source)

    # ------------------ 等待页面加载 ------------------
    # 使用 WebDriverWait 等待搜索输入框出现，这比 time.sleep() 更可靠
    try:
        wait = WebDriverWait(driver, 100)
        # time.sleep(1000)
        wait.until(EC.visibility_of_element_located((By.XPATH, "//img[@src='/images/carousel_pic1.jpg']")))


        link = driver.find_element(By.LINK_TEXT, "信息公开")
        link.click()
        print(driver.page_source)
        wait.until(EC.visibility_of_element_located((By.XPATH, "//li[text()='受理品种目录浏览']")))

        link = driver.find_element(By.LINK_TEXT, "药品目录集信息")
        link.click()

    except Exception as e:
        print(f"发生错误：{e}")
        # 如果出错，也可以选择关闭浏览器
        # driver.quit()


# 调用函数
if __name__ == "__main__":
    search_nmpa_drug()