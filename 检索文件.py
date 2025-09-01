import os
import json

base_path = r"E:\PROJECT\25_71_Robinagent\spider\data"

# 将目录里的文件以list的形式返回
for entry in os.listdir(base_path):
    # 只需要把文件名作为参数，自动构建完整路径
    entry_path = os.path.join(base_path, entry)

    # 在子文件夹中寻找 JSON 文件
    for filename in os.listdir(entry_path):
        # 检查文件是否以 d.json 结尾
        if not filename.endswith('d.json'):
            json_file_path = os.path.join(entry_path, filename)
            print(f"  正在读取文件: {json_file_path}")

            try:
                # 以 UTF-8 编码打开并读取 JSON 文件
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print("  文件读取成功！")

            except json.JSONDecodeError as e:
                print(f"  错误：文件 '{json_file_path}' 不是一个有效的 JSON 文件。错误信息：{e}")
            except Exception as e:
                print(f"  读取文件 '{json_file_path}' 时发生未知错误：{e}")
