import scrapy
import os
import json
import logging
import patent_stil
import pandas as pd
import os
import requests


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


compound_dir = r"E:\PROJECT\25_71_Robinagent\516541"
drug_list = os.listdir(r"E:\PROJECT\25_71_Robinagent\data")
for drug in drug_list:
    try:
        df = pd.read_csv(r"E:\PROJECT\25_71_Robinagent\516541\patent\pubchem_cid_92786_patent.csv")
        # 检查所需的列是否存在
        if 'publicationnumber' not in df.columns or 'title' not in df.columns:
            print("错误: CSV文件缺少'publicationnumber'或'title'列。")
        else:
            # 初始化目标数据结构
            patent_info = {}  # 字典，键为专利号，值为专利名
            patent_num = []  # 列表，只存专利号
            # 遍历 DataFrame 的每一行
            for index, row in df.iterrows():
                patent_number = str(row['publicationnumber']).replace("-", "")  # 获取专利号并移除破折号
                patent_title = str(row['title'])  # 获取专利名
                # 填充字典 patent_info
                patent_info[patent_number] = patent_title
                # 填充列表 patent_num
                patent_num.append(patent_number)
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
        res = patent_stil.getGooglePatentInfo(patent, language="auto", )# proxies=create_proxy_dict(res1.text))
        # 下载PDF，通过res.pdf_url获取专利地址，并且下载。
        pdf_path = os.path.join(r"E:\PROJECT\25_71_Robinagent\516541\patent", f"{patent}.pdf")
        patent_stil.downloadGooglePdf(res.pdf_url, save_path=os.path.join(os.path.join(compound_dir, "patent"),
                                                                          f"{res.title}.pdf"))


        # 获取专利信息。如果失败，res 可能会是 None
        res = patent_stil.getGooglePatentInfo(
            patent,
            language="auto",
        )
        #     proxies=create_proxy_dict(res1.text)
        # )

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

