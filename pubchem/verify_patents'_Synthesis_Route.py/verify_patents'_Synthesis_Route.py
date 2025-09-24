import os
from openai import OpenAI
import csv
import pandas as pd
client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key="sk-d84b710f6a4d40509aeacdbb6ffad309",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def get_response(title: str, abstract: str):
    if abstract != abstract:
        abstract = "None"
    completion = client.chat.completions.create(
        model="qwen3-235b-a22b-instruct-2507",
        messages=[
            {"role": "system", "content": "You are a Chemical expert."},
            {"role": "user",
             "content": "I will provide you with the title and abstract of the patent. Please help me determine whether this patent contains information about the synthesis route and whether it contains information about the synthesis mechanism. Please think step by step and reply to me in the format of a dict like{Synthesis Route: 1, Synthesis Mechanism: 1}. Patent Title:" + str(title) + "Patent Abstract:" + str(abstract)},
        ],
        stream=False
    )
    return completion.choices[0].message.content


df = pd.read_csv(r"/data_FDAJSON/63013/patent/63013patent.csv")
patents = df[["title", "abstract"]]
print(patents)
for row in patents.itertuples(index=False):
    # 通过属性名访问数据，非常清晰
    title = row.title
    abstract = row.abstract
    res = get_response(title,  abstract)
    print(res)


# with open(r"E:\PROJECT\25_71_Robinagent\data_FDAJSON\1254\patent\1254patent.csv", 'w',
#           newline='', encoding='utf-8-sig') as file:
#     # 1. 创建 writer 对象
#     writer = csv.writer(file)
#
#     # 2. 使用 writerows() 方法传入列表一次性写入多行
#     writer.writerows(data_to_write)
