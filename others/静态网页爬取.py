from bs4 import BeautifulSoup
import requests
import urllib.parse

url = "https://books.toscrape.com/catalogue/category/books/historical-fiction_4/index.html"
response = requests.get(url, timeout=(10, 30))
page = BeautifulSoup(response.text, 'html.parser')  # 解析html字符串

# todo:find()找到第一个匹配项，find_all()找出所有匹配项

# todo:需要先找到 <li> 标签内部的 <a> 标签，然后再从那个 <a> 标签中提取 href 属性。
elements = page.find_all('li', class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")
for elem in elements:
    tag = elem.find("a")
    src = tag.get("href")  # 获取相对路径

    # 使用 urllib.parse.urljoin 来拼接成完整的绝对URL
    # base_url 应该是当前列表页面的 URL
    full_url = urllib.parse.urljoin(url, src)
    print(f"找到的完整 href 链接:" + str(full_url))

    # todo:进入这本书的网页内部，爬取图片的url
    book_response = requests.get(full_url)
    book_page = page = BeautifulSoup(book_response.text, 'html.parser')
    jpg = book_page.find('div', class_="item active")
    tag = jpg.find('img')
    img_src = tag.get("src")
    print("img_src:     "+str(img_src))

    # 获取书名
    book_title_tag = elem.find('h3').find('a')
    if book_title_tag:
        book_title = book_title_tag.get('title')
        print(f"书名: {book_title}")

    # 获取价格
    price_tag = elem.find('p', class_='price_color')
    if price_tag:
        book_price = price_tag.get_text(strip=True)
        print(f"价格: {book_price}")


