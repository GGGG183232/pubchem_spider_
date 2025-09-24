import pandas as pd
import os

# --- 请确认这两个文件路径是正确的 ---
source_file_path = r'E:\PROJECT\25_71_Robinagent\data_111\4440\paper\4440paper.csv'
output_file_path = r'E:\PROJECT\25_71_Robinagent\spider\pubchem\pubchem_scrapy\pubchem_scrapy1\journal_source.csv'

try:
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建目录: {output_dir}")

    # 读取源CSV文件
    df = pd.read_csv(source_file_path)

    # 检查 'Publication_Name' 列是否存在
    if 'Publication_Name' in df.columns:
        # 提取 'Publication_Name' 这一列，并去除可能存在的前后空格
        publication_names = df['Publication_Name'].str.strip()

        # 使用 value_counts() 方法直接统计每个名称的出现次数
        counts_series = publication_names.value_counts()

        # 将统计结果的 Series 转换为 DataFrame
        # reset_index() 会将索引（Publication_Name）变成一列
        # 然后我们重命名列以匹配要求
        result_df = counts_series.reset_index()
        result_df.columns = ['Publication_Name', 'Count']  # 重命名列

        # 将结果 DataFrame 保存到新的 CSV 文件中
        # index=False 表示不将 DataFrame 的索引写入文件
        result_df.to_csv(output_file_path, index=False, encoding='utf-8-sig')

        print(f"统计成功！结果已保存到: {output_file_path}")

    else:
        print(f"错误：在文件 {source_file_path} 中没有找到名为 'Publication_Name' 的列。")
        print(f"可用的列有: {df.columns.tolist()}")

except FileNotFoundError:
    print(f"错误：找不到源文件，请检查路径是否正确: {source_file_path}")
except Exception as e:
    print(f"处理文件时发生未知错误: {e}")