import os
import json
import requests
import logging
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def crawl_pubchem_data(input_json_path, output_root_dir, crawl_options=None):
    """
    从本地 JSON 文件中读取 CID 列表，并爬取 PubChem 的化合物数据。
    每次请求后会暂停以控制爬取速度。

    Args:
        input_json_path (str): 包含药物 CID 信息的 JSON 文件路径。
        output_root_dir (str): 保存爬取数据的根目录。
        crawl_options (dict, optional): 爬取选项，
            包括 'basic_info'、'2d' 和 '3d'。默认为全部爬取。
    """
    # 默认爬取选项
    if crawl_options is None:
        crawl_options = {"basic_info": True, "2d": True, "3d": True}

    # API 端点
    base_url_view = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/"
    base_url_2d = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/CID/{cid}/record/JSON?record_type=2d"
    base_url_3d = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/CID/{cid}/record/JSON?record_type=3d"

    # 控制请求频率：每秒不超过5个请求，即每个请求间隔至少 0.2 秒
    request_delay = 1.0 / 5.0  # 1 / 5 = 0.2秒

    # 读取输入 JSON 文件
    try:
        with open(input_json_path, "r", encoding="utf-8") as f:
            catalogue = json.load(f)
        cid_list = [str(entry["pubchem_cid"]) for entry in catalogue if entry.get("pubchem_cid")]
        if not cid_list:
            logging.warning("在输入文件中未找到有效的 'pubchem_cid'，脚本退出。")
            return
        logging.info(f"共加载 {len(cid_list)} 个 CID 来爬取 PubChem 数据。")
    except FileNotFoundError:
        logging.error(f"错误：未找到文件 {input_json_path}")
        return
    except json.JSONDecodeError:
        logging.error(f"错误：文件 {input_json_path} 不是一个有效的 JSON 文件。")
        return

    # 遍历 CID 列表并爬取数据
    for cid in cid_list:
        logging.info(f"正在处理 CID: {cid}")
        compound_dir = os.path.join(output_root_dir, cid)
        os.makedirs(compound_dir, exist_ok=True)

        # 爬取主 JSON
        if crawl_options["basic_info"]:
            url = base_url_view.format(cid=cid)
            file_path = os.path.join(compound_dir, f"{cid}.json")
            download_json(url, file_path)
            time.sleep(request_delay)

        # 爬取 2D JSON
        if crawl_options["2d"]:
            url = base_url_2d.format(cid=cid)
            file_path = os.path.join(compound_dir, f"{cid}_2d.json")
            download_json(url, file_path)
            time.sleep(request_delay)

        # 爬取 3D JSON
        if crawl_options["3d"]:
            url = base_url_3d.format(cid=cid)
            file_path = os.path.join(compound_dir, f"{cid}_3d.json")
            download_json(url, file_path)
            time.sleep(request_delay)


def download_json(url, file_path):
    """
    使用 requests 库下载 JSON 数据并保存到文件。

    Args:
        url (str): 目标 URL。
        file_path (str): 保存文件的完整路径。
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 检查 HTTP 请求是否成功
        data = response.json()

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        logging.info(f"成功保存数据到 {file_path}")

    except requests.exceptions.RequestException as e:
        logging.error(f"请求 URL {url} 时发生错误: {e}")
    except json.JSONDecodeError:
        logging.warning(f"URL {url} 的响应内容不是有效的 JSON。")
    except Exception as e:
        logging.error(f"保存文件到 {file_path} 失败: {e}")


if __name__ == "__main__":
    # 定义输入和输出路径
    input_file = r"E:\PROJECT\25_71_Robinagent\spider\pubchem\drug_cataloge\drug_catalogue.json"
    output_directory = r"E:\PROJECT\25_71_Robinagent\pubchem_field2"

    # 定义爬取选项（可以根据需要修改）
    crawl_options_to_run = {
        "basic_info": True,
        "2d": True,
        "3d": False
    }

    crawl_pubchem_data(input_file, output_directory, crawl_options_to_run)