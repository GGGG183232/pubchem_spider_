"""
FDACSV
***************************
* PubChem 化合物 JSON + 2D/3D 数据爬取
* 数据源: 本地 drug_catalogue.json
* JSON 路径: E:\\PROJECT\\25_71_Robinagent\\spider\\pubchem\\drug_cataloge\\drug_catalogue.json
* 起始 URL:
    - https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{CID}/JSON/
    - https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/CID/{CID}/record/JSON?record_type=2d
    - https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/CID/{CID}/record/JSON?record_type=3d
* 保存目录: E:\\PROJECT\\25_71_Robinagent\\pubchem_field\\{CID}\\
***************************
"""
import scrapy
import os
import json
import logging
import patent_stil
import pandas as pd
import os
import requests


# todo:???from spider.pubchem.pubchem_scrapy.spiders import settings
# todo:???import settings

def create_proxy_dict(proxy_str):  # 构建proxy
    # Check if the input is a string and not empty
    if not isinstance(proxy_str, str) or not proxy_str.strip():
        logging.error("Input must be a non-empty string.")
        return None

    # Check if the string contains a colon to separate IP and port
    if ":" not in proxy_str:
        logging.error(f"Invalid proxy string format: '{proxy_str}'. Expected 'ip:port'.")
        return None
    proxy_dict = {
        "http": f"http://{proxy_str}",
        "https": f"http://{proxy_str}",
    }

    return proxy_dict


class PubchemSpider(scrapy.Spider):
    name = "FDACSV"  # 用于调用，scrapy crawl pubchem爬取
    base_url_view = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/?response_type=save&response_basename=COMPOUND_CID_{cid}"
    base_url_2d = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/CID/{cid}/record/JSON?record_type=2d&response_type=save&response_basename=Structure2D_COMPOUND_CID_{cid}"
    base_url_3d = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/CID/{cid}/record/JSON?record_type=3d&response_type=save&response_basename=Conformer3D_COMPOUND_CID_{cid}"
    base_url_patent = "https://pubchem.ncbi.nlm.nih.gov/sdq/sdqagent.cgi?infmt=json&outfmt=csv&query={{%22download%22:%22*%22,%22collection%22:%22patent%22,%22order%22:[%22prioritydate,desc%22],%22start%22:1,%22limit%22:10000000,%22downloadfilename%22:%22pubchem_cid_{cid}_patent%22,%22nullatbottom%22:1,%22where%22:{{%22ands%22:[{{%22cid%22:%22{cid}%22}}]}}}}&showcolumndisplayname=1"
    base_url_paper = "https://pubchem.ncbi.nlm.nih.gov/sdq/sdqagent.cgi?infmt=json&outfmt=csv&query={{%22download%22:%22*%22,%22collection%22:%22literature%22,%22order%22:[%22articlepubdate,desc%22],%22start%22:1,%22limit%22:10000000,%22downloadfilename%22:%22pubchem_cid_{cid}_literature%22,%22nullatbottom%22:1,%22where%22:{{%22ands%22:[{{%22cid%22:%22{cid}%22}}]}}}}&showcolumndisplayname=1"

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    def __init__(self, json_path=None, output_root=None, *args, **kwargs):
        super(PubchemSpider, self).__init__(*args, **kwargs)
        # 默认的 drug_catalogue.json 路径
        self.INPUT = r"E:\PROJECT\25_71_Robinagent\spider\pubchem\pubchem_scrapy\pubchem_scrapy1\FDA_getcid\20250915_095558.csv"
        self.OUTPUT = r"E:\PROJECT\25_71_Robinagent\data"
        # todo:
        # self.INPUT = r"/data/spider/Goujinhe/drug_catalogue.json"
        # self.OUTPUT = r"/data/spider/Goujinhe/pubchem_json"
        self.crawl = {"basic_info": True, "2d": False, "3d": False, "patent": True, "paper": True}
        self.json_path = self.INPUT
        # 固定保存路径
        self.output_root = output_root or self.OUTPUT
        # 读取 JSON 文件，提取 pubchem_cid
        df = pd.read_csv(self.INPUT)
        drug_cids = df["cid"]
        cid_list = []
        for drug_cid in drug_cids:
            if pd.isna(drug_cid):
                continue
            else:
                cid_list.append(str(int(drug_cid)))
        self.cid_list = list(set(cid_list))
        self.logger.info(f"共加载 {len(self.cid_list)} 个 CID 来爬取 PubChem 数据")

    def start_requests(self):
        for cid in self.cid_list:
            self.logger.info(f"正在处理 CID: {cid}")
            compound_dir = os.path.join(self.output_root, str(cid))
            os.makedirs(compound_dir, exist_ok=True)

            # 主 JSON
            if self.crawl['basic_info']:
                yield scrapy.Request(
                    self.base_url_view.format(cid=cid),
                    callback=self.save_file,
                    meta={'cid': cid, 'compound_dir': compound_dir, 'suffix': ""}
                )

            # 2D JSON
            if self.crawl['2d']:
                yield scrapy.Request(
                    self.base_url_2d.format(cid=cid),
                    callback=self.save_file,
                    meta={'cid': cid, 'compound_dir': compound_dir, 'suffix': "_2d"}
                )

            # 3D JSON
            if self.crawl["3d"]:
                yield scrapy.Request(
                    self.base_url_3d.format(cid=cid),
                    callback=self.save_file,
                    meta={'cid': cid, 'compound_dir': compound_dir, 'suffix': "_3d"}
                )

            if self.crawl["patent"]:
                yield scrapy.Request(
                    self.base_url_patent.format(cid=cid),
                    callback=self.save_file_patent,
                    meta={'cid': cid, 'compound_dir': compound_dir, 'suffix': "patent"}
                )

            if self.crawl["paper"]:
                yield scrapy.Request(
                    self.base_url_paper.format(cid=cid),
                    callback=self.save_file_paper,
                    meta={'cid': cid, 'compound_dir': compound_dir, 'suffix': "paper"}
                )

    def save_file(self, response):
        cid = response.meta['cid']
        compound_dir = response.meta['compound_dir']
        suffix = response.meta['suffix']  # "", "_2d", "_3d"

        json_path = os.path.join(compound_dir, f"{cid}{suffix}.json")

        # 检查响应是否为空
        if not response.text.strip():
            self.logger.warning(f"CID {cid}{suffix} 响应为空，跳过保存")
            return

        try:
            with open(json_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            self.logger.info(f"CID {cid}{suffix} 的 JSON 数据已保存到 {json_path}")
        except Exception as e:
            self.logger.error(f"CID {cid}{suffix} 保存 JSON 失败: {e}")

        yield {
            "cid": cid,
            "file": json_path
        }

    def save_file_patent(self, response):
        cid = response.meta['cid']
        compound_dir = response.meta['compound_dir']
        suffix = response.meta['suffix']  # "", "_2d", "_3d"
        os.makedirs(compound_dir, exist_ok=True)
        os.makedirs(os.path.join(compound_dir, "patent"), exist_ok=True)
        csv_path = os.path.join(compound_dir, "patent", f"{cid}{suffix}.csv")
        try:
            with open(csv_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            self.logger.info(f"CID 的 patent_csv 数据已保存到 {csv_path}")
        except Exception as e:
            self.logger.error(f"CID 保存 patent_csv 失败: {e}")

        try:
            df = pd.read_csv(csv_path)
            # 检查所需的列是否存在
            if 'publicationnumber' not in df.columns or 'title' not in df.columns:
                print("错误: CSV文件缺少'publicationnumber'或'title'列。")
            else:
                # 初始化目标数据结构
                patent_info = {}  # 字典，键为专利号，值为专利名
                patent_num = []  # 列表，只存专利号
                # 遍历 DataFrame 的每一行


                # todo:限制，每个药只爬10个专利
                count = 0
                for index, row in df.iterrows():
                    if count > 11:
                        break
                    else:
                        patent_number = str(row['publicationnumber']).replace("-", "")  # 获取专利号并移除破折号
                        patent_title = str(row['title'])  # 获取专利名
                        # 填充字典 patent_info
                        patent_info[patent_number] = patent_title
                        # 填充列表 patent_num
                        patent_num.append(patent_number)
                        count += 1
                print("专利信息字典 (patent_info):")
                # print(patent_info)
                print("\n专利号列表 (patent_num):")
                print("patent_num=" + str(len(patent_num)))
        except Exception as e:
            print(f"处理文件时发生错误: {e}")
        for patent in patent_num:
            # res1 = requests.get(
            #     r"https://www.kookeey.com/pickdynamicips?auth=ip&n=1&p=http&g=US&type=txt&sign=5ab92996e5458b42946b3196ac952b05&accessid=8966104&dl=\r\n")
            # print(res1.text)

            try:

                res = patent_stil.getGooglePatentInfo(patent, language="auto")# , proxies=create_proxy_dict(res1.text))
                # 下载PDF，通过res.pdf_url获取专利地址，并且下载。
                pdf_path = os.path.join(r"E:\PROJECT\25_71_Robinagent\mypack", f"{patent}.pdf")
                patent_stil.downloadGooglePdf(res.pdf_url, save_path=os.path.join(os.path.join(compound_dir, "patent"),
                                                                                  f"{res.title}.pdf"))


                # 获取专利信息。如果失败，res 可能会是 None
                res = patent_stil.getGooglePatentInfo(
                    patent,
                    language="auto",
                    # todo:proxies=create_proxy_dict(res1.text)
                )

                # 检查 res 是否为 None。如果为 None，则会触发下面的 except 块
                if res is None:
                    raise ValueError("GooglePatentInfo returned None")

                pdf_path = os.path.join(
                    os.path.join(compound_dir, "patent"),
                    f"{patent}.pdf"
                )
                patent_stil.downloadGooglePdf(
                    res.pdf_url,
                    save_path=os.path.join(os.path.join(compound_dir, "patent"), f"{res.title}.pdf")
                )

            except Exception as e:
                # 如果 res 为 None，或者在处理过程中发生其他错误，这个 except 块会被执行
                print(f"res = {patent} 下载失败: {e}")

        yield {
            "cid": cid,
            "file": csv_path
        }

    def save_file_paper(self, response):
        cid = response.meta['cid']
        compound_dir = response.meta['compound_dir']
        suffix = response.meta['suffix']  # "", "_2d", "_3d"
        os.makedirs(os.path.join(compound_dir, "paper"), exist_ok=True)
        csv_path = os.path.join(compound_dir, "paper", f"{cid}{suffix}.csv")
        try:
            with open(csv_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            self.logger.info(f"CID 的 paper_csv 数据已保存到 {csv_path}")
        except Exception as e:
            self.logger.error(f"CID 保存 paper_csv 失败: {e}")

        pass
