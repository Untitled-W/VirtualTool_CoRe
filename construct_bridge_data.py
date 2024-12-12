import json
from tqdm import trange
from utils import list2array, random_move_original_bridge, add_noise_bridge, add_random_obj, build_bridge_data

file_dir = './tool-games/environment/Trials/Original/Bridge.json'

scenes = []

with open(file_dir, 'r') as f:
    file = json.load(f)

for index in trange(10000):
    objects = []
    # 随机移动基础场景：
    file = random_move_original_bridge(file)
    
    # 添加相似干扰项：
    file, objects = add_noise_bridge(file, objects)

    # 添加随机干扰项：
    file, objects = add_random_obj(file, objects)

    objects = build_bridge_data(file, objects)

    scene = {
        "scene_id": index,
        "objects": objects
    }
    scenes.append(scene)

with open('./bridge_data.json', 'w') as f:
    json.dump(scenes, f)