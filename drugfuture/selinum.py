import csv
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# --- 1. 配置信息 ---
# 使用r"..."原始字符串来处理Windows路径，避免转义符问题
CSV_FILE_PATH = r"E:\PROJECT\25_71_Robinagent\spider\drugfuture\chemical_substances.csv"
HTML_SAVE_BASE_PATH = r"E:\PROJECT\25_71_Robinagent\drugfuture_html"
BASE_URL = "https://www.drugfuture.com/synth/synth_query.asp"


def process_drug(driver, drug_name, save_base_path):
    """
    处理单个药品的完整流程：搜索、保存详情页、点击路线、保存路线页。

    :param driver: Selenium WebDriver 实例。
    :param drug_name: 从CSV中读取的药品名称。
    :param save_base_path: HTML文件的根保存路径。
    """
    try:
        print(f"\n--- 开始处理药品: {drug_name} ---")

        # 步骤A：导航到搜索页面
        driver.get(BASE_URL)

        # 步骤B：输入药品名并搜索
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "DRUG_NAME"))
        )
        search_box.clear()  # 清空搜索框，以防上次输入残留
        search_box.send_keys(drug_name)

        submit_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"][value="查询"]')
        submit_button.click()

        # 步骤C：保存详情页HTML
        # 等待页面跳转后某个元素出现，以确认页面加载
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        # 创建用于保存的文件夹
        save_dir = os.path.join(save_base_path, drug_name.strip())
        os.makedirs(save_dir, exist_ok=True)

        detail_page_path = os.path.join(save_dir, 'detail.html')
        with open(detail_page_path, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print(f"  [成功] 已保存详情页: {detail_page_path}")

        # 步骤D：查找并点击合成路线链接，然后保存路线页HTML
        try:
            # 使用更灵活的链接文本查找，因为ID可能变化
            synthesis_link = WebDriverWait(driver, 5).until(  # 使用较短的超时时间
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "查看合成路线"))
            )
            synthesis_link.click()

            # 等待新页面加载完成 (例如，等待标题改变)
            time.sleep(15)

            route_page_path = os.path.join(save_dir, 'route.html')
            with open(route_page_path, 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print(f"  [成功] 已保存路线页: {route_page_path}")

        except TimeoutException:
            print(f"  [警告] 未找到 '{drug_name}' 的合成路线链接，跳过保存路线页。")

    except Exception as e:
        print(f"  [错误] 处理 '{drug_name}' 时发生意外错误: {e}")


def main():
    """
    主函数，负责初始化、读取CSV和循环处理。
    """
    # 初始化 WebDriver
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    try:
        # 读取CSV文件
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8-sig') as csvfile:  # 使用 'utf-8-sig' 避免BOM问题
            reader = csv.DictReader(csvfile)
            drug_names = [row['name'] for row in reader if row.get('name')]

        print(f"成功从CSV加载 {len(drug_names)} 个药品名称。")

        # 循环处理每个药品
        for name in drug_names:
            process_drug(driver, name.strip(), HTML_SAVE_BASE_PATH)

    finally:
        # 确保浏览器被关闭
        print("\n所有任务已完成，关闭浏览器。")
        driver.quit()


if __name__ == '__main__':
    main()