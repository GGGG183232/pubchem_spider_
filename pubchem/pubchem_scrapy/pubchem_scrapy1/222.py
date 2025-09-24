import os
import requests

names = ["aspirin", "acetaminophen", "ibuprofen"]           # 需要检索的化合物英文
base_url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{}/property/CanonicalSMILES,title/CSV'
headers = {"content-type":"application/x-www-form-urlencoded"}
file_path = 'result_by_name.csv'                            # 输出文件，每次运行前需要删除上一次运行存在的输出

# 检查文件是否存在且为空，如果是，则只在文件开头写入标题行
if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
    with open(file_path, 'w', encoding='UTF8') as f:
        f.write('"CID","CanonicalSMILES","Title"\n')

for name in names:
    url = base_url.format(name)
    res = requests.get(url, headers=headers)
    # 分割响应文本以跳过标题行，然后将剩余部分写入文件，不添加额外的空行
    data_lines = res.text.strip().split('\n')[1:]  # 移除首尾空白字符，并分割文本以跳过标题行
    if data_lines:  # 确保data_lines不为空
        with open(file_path, 'a', encoding='UTF8') as f:
            f.write('\n'.join(data_lines) + '\n')  # 写入数据行，每行之后直接跟换行符

