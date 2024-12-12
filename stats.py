import os
import json
from collections import Counter

def get_object_types_from_json(folder_path):
    # 用于统计所有 type 的计数
    type_counter = Counter()

    # 遍历文件夹中的所有文件
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.json'):
            file_path = os.path.join(folder_path, file_name)
            try:
                # 读取 JSON 文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 检查是否包含 objects 字段
                if "world" in data and "objects" in data["world"]:
                    objects = data["world"]["objects"]
                    # 遍历 objects 并统计 type
                    for obj_name, obj_info in objects.items():
                        obj_type = obj_info.get("type", "Unknown")
                        type_counter[obj_type] += 1
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")
    
    return type_counter

# 指定文件夹路径
folder_path = "E:/vscode/CoRe/VirtualTool_CoRe/tool-games/environment/Trials/Original/"

# 获取所有对象类型的统计信息
type_statistics = get_object_types_from_json(folder_path)

# 打印统计结果
print("Object Type Statistics:")
for obj_type, count in type_statistics.items():
    print(f"{obj_type}: {count}")
