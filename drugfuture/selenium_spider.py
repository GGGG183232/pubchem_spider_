from selenium import webdriver
import os
import pandas
import csv
from selenium.common.exceptions import TimeoutException # 需要导入这个异常类

driver = webdriver.Chrome()
save_dir = r"E:\PROJECT\25_71_Robinagent\drugfuture_html"
input_dir = r"E:\PROJECT\25_71_Robinagent\spider\drugfuture\chemical_substances.csv"





def process_drug(driver, name, save_dir):


    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By

    # 由于动态网页的加载是异步进行的，通常需要等待一段时间才能确保所有内容都已加载完成。可以使用Selenium提供的等待机制来实现。
    # 等待10秒钟，直到某个元素可见
    # 指定使用 XPath 的方式来查找
    # //div[@class='dynamic-content']": 这是一个 XPath 表达式，它的意思是：//: 在整个页面的任意位置开始搜索。div: 寻找一个 <div> 标签。
    # [@class='dynamic-content']: 这个 <div> 标签必须有一个 class 属性，并且这个属性的值正好等于 'dynamic-content'
    wait = WebDriverWait(driver, 10)
    # element = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='dynamic-content']")))


    # 两种定位方式，上面这种更加可靠，因为因为会等看到 DRUG NAME 标签后才会输入阿司匹林
    # element = wait.until(EC.visibility_of_element_located((By.NAME, "DRUG_NAME")))
    element = driver.find_element(By.NAME, "DRUG_NAME")
    element.send_keys(name)

    # 点击按钮  <input type="submit" value="查询">
    # css selector可以组合 type 和 value 两个属性来精确定位
    submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='查询']")
    submit_button.click()

    # 等待页面加载出来 tag name为标签名，<p>中的p
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "head")))

    try:
        # 步骤1：将可能会出错的代码放入 try 代码块中
        print("  正在等待'分子量'标签加载...")
        wait.until(EC.visibility_of_element_located((By.XPATH, "//td[contains(text(), '分子量')]")))
        print("  '分子量'标签已成功加载。")

    except TimeoutException:
        # 步骤2：如果 try 代码块中发生了 TimeoutException，程序不会崩溃，而是会执行这里的代码
        print(f"  [警告] 未找到'分子量'标签，可能没有该药品信息。")
        print("  跳过当前药品...")
        return # 循环立刻进入下一次迭代

    print("正在保存当前页面的HTML...")

    # 您可以为文件命名，例如 'synthesis_route.html'
    html_file_path = os.path.join(save_dir, name+'info.html')

    # 使用我们熟悉的方法写入文件
    with open(html_file_path, 'w', encoding='utf8') as f:
        f.write(driver.page_source)

    print(f"  [成功] 页面HTML已保存到: {html_file_path}")


    submit_button = driver.find_element(By.XPATH, "//a[text()='查看合成路线']")
    submit_button.click()


    print("正在等待'//td[contains(text(), '合成路线图解说明')]'标签加载...")
    new_new_page = wait.until(EC.visibility_of_element_located((By.XPATH, "//td[contains(text(), '合成路线图解说明')]")))
    print("'//td[contains(text(), '合成路线图解说明')]'标签已成功加载并可见。")


    # 您可以为文件命名，例如 'synthesis_route.html'
    html_file_path = os.path.join(save_dir, name+'synthesis_route'+'.html')

    # 使用我们熟悉的方法写入文件
    with open(html_file_path, 'w', encoding='utf8') as f:
        f.write(driver.page_source)




if __name__ == '__main__':
    # 使用WebDriver对象的get()方法加载目标动态网页
    # 创建一个WebDriver对象来控制浏览器的行为
    # 创建Chrome WebDriver对象
    url = "https://www.drugfuture.com/synth/synth_query.asp"  # 目标动态网页的URL
    driver.get(url) # todo:构建driver对象，将这个对象传入方法中用于遍历，这样就不用每次重新加载浏览器

    with open(input_dir, mode='r', encoding='utf-8-sig') as csvfile:  # 使用 'utf-8-sig' 避免BOM问题
        reader = csv.DictReader(csvfile)
        drug_names = [row['name'] for row in reader if row.get('name')]

    print(f"成功从CSV加载 {len(drug_names)} 个药品名称。")

    # 循环处理每个药品
    for name in drug_names:
        process_drug(driver, name.strip(), save_dir)
        driver.get(url)  # todo: <-- 核心修复：每次循环都重新访问搜索页面,不然的话从一个网页退出就找不到下一个网页了