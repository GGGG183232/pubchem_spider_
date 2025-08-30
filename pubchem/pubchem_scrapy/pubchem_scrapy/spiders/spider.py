"""
***************************
* PubChem 化合物 JSON + 2D/3D 数据爬取
* 数据源: 本地 drug_catalogue.json
* JSON 路径: E:\\PROJECT\\25_71_Robinagent\\spider\\pubchem\\drug_cataloge\\drug_catalogue.json
* 起始 URL:
    - https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{CID}/JSON/
    - https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/CID/{CID}/record/JSON?record_type=2d
    - https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/CID/{CID}/record/JSON?record_type=3d
* 保存目录: E:\\PROJECT\\25_71_Robinagent\\pubchem_field\\{CID}\\
* author: ChatGPT
***************************
"""
import scrapy
import os
import json


class PubchemSpider(scrapy.Spider):
    name = "pubchem"
    base_url_view = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/?response_type=save&response_basename=COMPOUND_CID_{cid}"
    # base_url_view = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/"
    # base_url_2d = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/CID/{cid}/record/JSON?record_type=2d"
    # base_url_3d = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/CID/{cid}/record/JSON?record_type=3d"
    base_url_2d = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/CID/{cid}/record/JSON?record_type=2d&response_type=save&response_basename=Structure2D_COMPOUND_CID_{cid}"
    base_url_3d = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/CID/{cid}/record/JSON?record_type=3d&response_type=save&response_basename=Conformer3D_COMPOUND_CID_{cid}"



    def __init__(self, json_path=None, output_root=None, *args, **kwargs):
        super(PubchemSpider, self).__init__(*args, **kwargs)
        # 默认的 drug_catalogue.json 路径
        self.json_path = json_path or r"E:\PROJECT\25_71_Robinagent\spider\pubchem\drug_cataloge\drug_catalogue.json"
        # 固定保存路径
        self.output_root = output_root or r"E:\PROJECT\25_71_Robinagent\pubchem_field"

        # 读取 JSON 文件，提取 pubchem_cid
        with open(self.json_path, "r", encoding="utf-8") as f:
            self.catalogue = json.load(f)

        # 只取有 pubchem_cid 的药物
        self.cid_list = [str(entry["pubchem_cid"]) for entry in self.catalogue if entry.get("pubchem_cid")]

        self.logger.info(f"共加载 {len(self.cid_list)} 个 CID 来爬取 PubChem 数据")

    def start_requests(self):
        for cid in self.cid_list:
            self.logger.info(f"正在处理 CID: {cid}")
            compound_dir = os.path.join(self.output_root, cid)
            os.makedirs(compound_dir, exist_ok=True)

            # 主 JSON
            yield scrapy.Request(
                self.base_url_view.format(cid=cid),
                callback=self.save_file,
                meta={'cid': cid, 'compound_dir': compound_dir, 'suffix': ""}
            )

            # 2D JSON
            yield scrapy.Request(
                self.base_url_2d.format(cid=cid),
                callback=self.save_file,
                meta={'cid': cid, 'compound_dir': compound_dir, 'suffix': "_2d"}
            )

            # 3D JSON
            yield scrapy.Request(
                self.base_url_3d.format(cid=cid),
                callback=self.save_file,
                meta={'cid': cid, 'compound_dir': compound_dir, 'suffix': "_3d"}
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
