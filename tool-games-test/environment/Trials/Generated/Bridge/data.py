import os
import shutil

# 定义文件夹路径
ball_folder = "./ball"
flip_folder = "./flip"
move_folder = "./move"
output_folder = "./data"

# 创建输出文件夹（如果不存在）
os.makedirs(output_folder, exist_ok=True)

# 函数：复制文件到目标文件夹
def copy_files(source_folder, start_index):
    files = [f for f in os.listdir(source_folder) if f.endswith(".json")]
    files = sorted(files, key=lambda x: int(x.split(".")[0]))  # 按数字排序
    
    current_index = start_index
    for file in files:
        src_path = os.path.join(source_folder, file)
        dst_path = os.path.join(output_folder, f"{current_index}.json")
        shutil.copy(src_path, dst_path)
        current_index += 1
    return current_index

# 从 1 开始编号
index = 1

# 遍历 ball 文件夹
index = copy_files(ball_folder, index)

# 遍历 move 文件夹
index = copy_files(move_folder, index)

# 遍历 flip 文件夹
index = copy_files(flip_folder, index)
