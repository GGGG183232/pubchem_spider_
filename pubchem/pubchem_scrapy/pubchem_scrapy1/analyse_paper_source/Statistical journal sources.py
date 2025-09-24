import csv
from collections import Counter

# --- 请将这里的文件路径替换为您自己的文件路径 ---
file_path = r'/data_111/4440/paper/4440paper.csv'

publication_list = []



def dict_to_csv(data_dict, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerows(data_dict.items())
def dict_to_csv_sorted(data_dict, filename):
    sorted_items = sorted(data_dict.items(), key=lambda item: item[1], reverse=True)
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerows(sorted_items)

try:
    # 打开并读取CSV文件，使用 utf-8 编码以避免乱码问题
    with open(file_path, mode='r', encoding='utf-8', newline='') as file:
        reader = csv.reader(file)

        # 读取表头
        header = next(reader)

        # 找到 'Publication_Name' 所在的列索引
        if 'Publication_Name' in header:
            name_index = header.index('Publication_Name')

            # 遍历文件的每一行，提取该列的数据
            for row in reader:
                # 确保行中有足够的列
                if len(row) > name_index:
                    publication_list.append(row[name_index].strip())

            # 使用 Counter 来统计列表中每个元素的出现次数
            counts_dict = Counter(publication_list)
            dict_to_csv_sorted(counts_dict, r'journal_source.csv')



            # 打印结果字典
            print("统计结果如下：")
            print(dict(counts_dict))  # 将 Counter 对象转换为普通字典

        else:
            print(f"错误：在文件 {file_path} 中没有找到名为 'Publication_Name' 的列。")
            print(f"可用的列有: {header}")

except FileNotFoundError:
    print(f"错误：找不到文件，请检查路径是否正确: {file_path}")
except Exception as e:
    print(f"处理文件时发生未知错误: {e}")