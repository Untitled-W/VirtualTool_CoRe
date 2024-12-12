import numpy as np
import pygame as pg
import json
import cv2
from tqdm import trange
from pyGameWorld.viewer import drawWorld, loadFromDict

def random_move_original_bridge(file):
    base_height = np.random.randint(80, 200)
    slide_height = np.random.randint(100, 200)
    ball_x = np.random.randint(550, 580)
    ball_y = np.random.randint(base_height + slide_height + 50, base_height + slide_height + 100)
    bridge_height = np.random.randint(10, 100)
    bridge_solid_height = np.random.randint(7, 10)
    goal_width = np.random.randint(35, 190)
    gap_width = np.random.randint(160, 600 - goal_width - 10 - 50 - 100)
    leftwall_width = np.random.randint(50, 600 - goal_width - 10 - gap_width - 100)
    bridge_edge = np.random.randint(70, gap_width - 70)
    leftwall_2_width = np.random.randint(max(10, leftwall_width - (bridge_edge - 10) * 0.5), leftwall_width - 8)
    rightwall_2_width = np.random.randint(max(80, 600 - goal_width - 10 - leftwall_width - gap_width - (gap_width - bridge_edge - 10) * 0.5), 600 - goal_width - 10 - leftwall_width - gap_width - 8)

    file['world']['objects']['Goal']['points'] = [[5, base_height + 5], [5, 5], [5 + goal_width, 5], [5 + goal_width, base_height + 5]]
    file['world']['objects']['LeftWall1']['vertices'] = [[goal_width + 10, 0], [goal_width + 10, base_height], [goal_width + 10 + leftwall_width, base_height], [goal_width + 10 + leftwall_width, 0]]
    file['world']['objects']['LeftWall2']['vertices'] = [[goal_width + 10, base_height], [goal_width + 10, base_height + bridge_solid_height], [goal_width + 10 + leftwall_2_width, base_height + bridge_solid_height], [goal_width + 10 + leftwall_2_width, base_height]]
    file['world']['objects']['RightWall1']['vertices'] = [[goal_width + 10 + leftwall_width + gap_width, 0], [goal_width + 10 + leftwall_width + gap_width, base_height], [600, base_height], [600, 0]]
    file['world']['objects']['RightWall2']['vertices'] = [[600 - rightwall_2_width, base_height], [600 - rightwall_2_width, base_height + bridge_solid_height], [600, base_height + bridge_solid_height + slide_height], [600, base_height]]
    file['world']['objects']['BridgeL']['vertices'] = [[goal_width + 10 + leftwall_2_width + 2, base_height + bridge_height], [goal_width + 10 + leftwall_2_width + 2, base_height + bridge_solid_height + bridge_height], [goal_width + 10 + leftwall_width + bridge_edge, base_height + bridge_solid_height + bridge_height], [goal_width + 10 + leftwall_width + bridge_edge, base_height + bridge_height]]
    file['world']['objects']['BridgeR']['vertices'] = [[goal_width + 10 + leftwall_width + bridge_edge + 2, base_height + bridge_height], [goal_width + 10 + leftwall_width + bridge_edge + 2, base_height + bridge_solid_height + bridge_height], [600 - rightwall_2_width - 2, base_height + bridge_solid_height + bridge_height], [600 - rightwall_2_width - 2, base_height + bridge_height]]
    file['world']['objects']['Ball']['position'] = [ball_x, ball_y]
    file['tools']['obj1'] = [[[-30, -base_height // 2], [-30, base_height // 2], [30, base_height // 2], [30, -base_height // 2]]]
    file['tools']['obj2'] = [[[-5, -base_height // 2], [-5, base_height // 2], [5, base_height // 2], [5, -base_height // 2]]]
    file['tools']['obj3'] = [[[-30, -30], [-30, 30], [30, 30], [30, -30]]]

    return file

def random_move_original_catapult(file):
    # 随机移动基础场景：
    base_height = np.random.randint(80, 250)
    left_pillar_height_diff = np.random.randint(2, 6)
    goal_short_width = np.random.randint(35, 100)
    goal_long_width = np.random.randint(goal_short_width + 10, goal_short_width + 60)
    goal_height = np.random.randint(base_height + 10, base_height + 50)
    catapult_vertical_width = np.random.randint(5, 15)
    catapult_horizon_width = np.random.randint(5, 15)
    catapult_vertical_length = np.random.randint(30, 45)
    catapult_horizon_length = np.random.randint(160, 300)
    gap_width = np.random.randint(45, 600 - 20 - goal_long_width - 5 - catapult_horizon_length - catapult_vertical_width)
    left_pillar_width = np.random.randint(10, 40)
    right_pillar_width = np.random.randint(10, 40)
    gap_between_pillar_width = np.random.randint(int(0.5 * catapult_horizon_length) - left_pillar_width - right_pillar_width, catapult_horizon_length - left_pillar_width - right_pillar_width - 60)
    right_pillar_x_min = 600 - goal_long_width - 5 - gap_width - catapult_horizon_length - catapult_vertical_width + left_pillar_width + gap_between_pillar_width
    right_pillar_x_max = right_pillar_x_min + right_pillar_width
    right_pillar_y_min = 0
    right_pillar_y_max = base_height
    left_pillar_x_min = 600 - goal_long_width - 5 - gap_width - catapult_horizon_length - catapult_vertical_width
    left_pillar_x_max = left_pillar_x_min + left_pillar_width
    left_pillar_y_min = 0
    left_pillar_y_max = base_height - left_pillar_height_diff
    ball_x = np.random.randint(left_pillar_x_min + catapult_vertical_width + 20, left_pillar_x_min + catapult_vertical_width + 20 + 30)
    ball_y = np.random.randint(base_height + 20 + catapult_horizon_width, base_height + 20 + catapult_horizon_width + 20)

    file['world']['objects']['Strut']['vertices'] = [[right_pillar_x_min, right_pillar_y_min], [right_pillar_x_min, right_pillar_y_max], [right_pillar_x_max, right_pillar_y_max], [right_pillar_x_max, right_pillar_y_min]]
    file['world']['objects']['Cradle']['vertices'] = [[left_pillar_x_min, left_pillar_y_min], [left_pillar_x_min, left_pillar_y_max], [left_pillar_x_max, left_pillar_y_max], [left_pillar_x_max, left_pillar_y_min]]
    file['world']['objects']['Goal']['points'] = [[600 - goal_long_width, goal_height], [600 - goal_short_width, 2], [598, 2], [598, goal_height]]
    file['world']['objects']['Catapult']['polys'] = [[[left_pillar_x_min, base_height], [left_pillar_x_min, base_height + catapult_horizon_width], [left_pillar_x_min + catapult_vertical_width, base_height + catapult_horizon_width], [left_pillar_x_min + catapult_vertical_width, base_height]], [[left_pillar_x_min, base_height + catapult_horizon_width], [left_pillar_x_min, base_height + catapult_horizon_width + catapult_vertical_length], [left_pillar_x_min + catapult_vertical_width, base_height + catapult_horizon_width + catapult_vertical_length], [left_pillar_x_min + catapult_vertical_width, base_height + catapult_horizon_width]], [[left_pillar_x_min + catapult_vertical_width, base_height], [left_pillar_x_min + catapult_vertical_width, base_height + catapult_horizon_width], [left_pillar_x_min + catapult_vertical_width + catapult_horizon_length, base_height + catapult_horizon_width], [left_pillar_x_min + catapult_vertical_width + catapult_horizon_length, base_height]]]
    file['world']['objects']['Ball']['position'] = [ball_x, ball_y]
    return file

def add_noise_bridge(file, objects, num=3):
    for i in range(num):
        item = {}
        noise_bridge_height = np.random.randint(7, 15)
        noise_bridge_bottom = np.random.randint(5, 590-noise_bridge_height)
        noise_bridge_len = np.random.randint(70, 150)
        noise_bridge_left = np.random.randint(5, 500-2*noise_bridge_len)
        Bridge_L = {
                "type": "Poly",
                "color": "blue",
                "density": 1,
                "vertices": [
                    [
                        noise_bridge_left,
                        noise_bridge_bottom
                    ],
                    [
                        noise_bridge_left,
                        noise_bridge_bottom + noise_bridge_height
                    ],
                    [
                        noise_bridge_left + noise_bridge_len,
                        noise_bridge_bottom + noise_bridge_height
                    ],
                    [
                        noise_bridge_left + noise_bridge_len,
                        noise_bridge_bottom
                    ]
                ]
            }
        Bridge_R = {
                "type": "Poly",
                "color": "blue",
                "density": 1,
                "vertices": [
                    [
                        noise_bridge_left + noise_bridge_len + 2,
                        noise_bridge_bottom
                    ],
                    [
                        noise_bridge_left + noise_bridge_len + 2,
                        noise_bridge_bottom + noise_bridge_height
                    ],
                    [
                        noise_bridge_left + 2*noise_bridge_len + 2,
                        noise_bridge_bottom + noise_bridge_height
                    ],
                    [
                        noise_bridge_left + 2*noise_bridge_len + 2,
                        noise_bridge_bottom
                    ]
                ]
            }
        # print(Bridge_L["vertices"])
        # print(Bridge_R["vertices"])
        file['world']['objects'][f"NoiseBridge{i}_L"] = Bridge_L
        file['world']['objects'][f"NoiseBridge{i}_R"] = Bridge_R

        item["item"] = list2array(0, Bridge_L["vertices"], 1)
        item["label"] = 0
        objects.append(item)
        item["item"] = list2array(0, Bridge_R["vertices"], 1)
        item["label"] = 0
        objects.append(item)
    return file, objects

def add_noise_catapult(file, objects, num=3):
    # 添加相似干扰项：
    for i in range(num):
        item = {}
        noise_height_1 = np.random.randint(10, 30)
        noise_height_2 = np.random.randint(1, 10)
        noise_length_1 = np.random.randint(30, 45)
        noise_length_2 = np.random.randint(160, 300)
        bottom = np.random.randint(1, 590-noise_height_1)
        left = np.random.randint(1, 590-noise_length_2)
        noise_Catapult = {
                "type": "Compound",
                "color": "blue",
                "density": 1,
                "polys": [
                    [
                        [
                            left,
                            bottom
                        ],
                        [
                            left,
                            bottom + noise_height_2
                        ],
                        [
                            left + noise_length_1,
                            bottom + noise_height_2
                        ],
                        [
                            left + noise_length_1,
                            bottom
                        ],
                    ],
                    [
                        [
                            left,
                            bottom + noise_height_2
                        ],
                        [
                            left,
                            bottom + noise_height_1
                        ],
                        [
                            left + noise_length_1,
                            bottom + noise_height_1
                        ],
                        [
                            left + noise_length_1,
                            bottom + noise_height_2
                        ],
                    ],
                    [
                        [
                            left + noise_length_1,
                            bottom
                        ],
                        [
                            left + noise_height_1,
                            bottom + noise_height_2
                        ],
                        [
                            left + noise_length_2,
                            bottom + noise_height_2
                        ],
                        [
                            left + noise_length_2,
                            bottom
                        ],
                    ]
                ]
            }

        file['world']['objects'][f"NoiseCatapult{i}"] = noise_Catapult
        item["item"] = list2array(2, noise_Catapult["polys"], 1)
        item["label"] = 0
        objects.append(item)
    return file, objects

def add_random_obj(file, objects, num=3):
    for i in range(num):
        item = {}
        random_width = np.random.randint(20, 120)
        random_height = np.random.randint(20, 120)
        random_x = np.random.randint(1, 600-random_width)
        random_y = np.random.randint(1, 600-random_height)
        random_obj = {
                "type": "Poly",
                "color": "black",
                "density": 0,
                "vertices": [
                    [
                        random_x,
                        random_y
                    ],
                    [
                        random_x,
                        random_y + random_height
                    ],
                    [
                        random_x + random_width,
                        random_y + random_height
                    ],
                    [
                        random_x + random_width,
                        random_y
                    ]
                ]
            }
        file['world']['objects'][f"RandomOBJ{i}"] = random_obj
        item["item"] = list2array(0, random_obj["vertices"], 0)
        item["label"] = 0
        objects.append(item)

    for i in range(num):
        random_width = np.random.randint(20, 120)
        random_height_1 = np.random.randint(20, 120)
        random_height_2 = np.random.randint(20, 120)
        random_x = np.random.randint(1, 600-random_width)
        random_y = np.random.randint(1, 600-random_height_1)
        random_obj = {
                "type": "Poly",
                "color": "black",
                "density": 0,
                "vertices": [
                    [
                        random_x,
                        random_y
                    ],
                    [
                        random_x,
                        random_y + random_height_1
                    ],
                    [
                        random_x + random_width,
                        random_y + random_height_2
                    ],
                    [
                        random_x + random_width,
                        random_y
                    ]
                ]
            }
        file['world']['objects'][f"RandomOBJ{i+3}"] = random_obj
        item["item"] = list2array(1, random_obj["vertices"], 0)
        item["label"] = 0
        objects.append(item)
    return file, objects

def build_bridge_data(file, objects):
    for data in file['world']['objects']:
        item = {}
        if data == 'Ball':
            info = list2array(3, [file['world']['objects'][data]['position'][0], file['world']['objects'][data]['position'][1], file['world']['objects'][data]['radius']], 1)
            item["item"] = info
            item["label"] = 0
        elif data == 'Goal':
            info = list2array(4, file['world']['objects'][data]['points'], 0)
            item["item"] = info
            item["label"] = 0
        elif data == 'BridgeL' or data == 'BridgeR':
            info = list2array(0, file['world']['objects'][data]['vertices'], 1)
            item["item"] = info
            item["label"] = 1
        elif data == 'LeftWall1' or data == 'LeftWall2' or data == 'RightWall1':
            info = list2array(0, file['world']['objects'][data]['vertices'], 0)
            item["item"] = info
            item["label"] = 1
        elif data == 'RightWall2':
            info = list2array(1, file['world']['objects'][data]['vertices'], 0)
            item["item"] = info
            item["label"] = 1
        elif data == "_LeftWall" or data == "_RightWall" or data == "_TopWall" or data == "_BottomWall":
            info = list2array(0, file['world']['objects'][data]['vertices'], 0)
            item["item"] = info
            item["label"] = 0
        else:
            continue
        objects.append(item)
    return objects

def build_catapult_data(file, objects):
    for data in file['world']['objects']:
        item = {}

        if data == 'Strut':
            item["item"] = list2array(0, file['world']['objects'][data]['vertices'], 0)
            item["label"] = 1
        elif data == 'Cradle':
            item["item"] = list2array(0, file['world']['objects'][data]['vertices'], 0)
            item["label"] = 1
        elif data == 'Goal':
            item["item"] = list2array(4, file['world']['objects'][data]['points'], 0)
            item["label"] = 0
        elif data == 'Catapult':
            item["item"] = list2array(2, file['world']['objects'][data]['polys'], 0)
            item["label"] = 1
        elif data == 'Ball':
            item["item"] = list2array(3, [file['world']['objects'][data]['position'][0], file['world']['objects'][data]['position'][1], file['world']['objects'][data]['radius']], 1)
            item["label"] = 0
        elif data == "_LeftWall" or data == "_RightWall" or data == "_TopWall" or data == "_BottomWall":
            info = list2array(0, file['world']['objects'][data]['vertices'], 0)
            item["item"] = info
            item["label"] = 0
        else:
            continue
        objects.append(item)
    return objects

def list2array(classtype, vertices, dynamictype):
    # 0: 矩形 1：梯形 2：compound 3:球 4: Goal
    if classtype == 0:
        # 返回形状类型，中心点坐标，长，宽，动态类型，标签
        return np.array([0, (vertices[0][0] + vertices[2][0])/2, (vertices[0][1] + vertices[2][1])/2, (-vertices[0][0] + vertices[2][0]), (-vertices[0][1] + vertices[2][1]), 0, 0, dynamictype]).tolist()
    elif classtype == 1:
        # 返回形状类型，左下角点坐标，长，长边宽，短边宽，动态类型，标签
        return np.array([1, vertices[0][0], vertices[0][1], (-vertices[0][0] + vertices[2][0]), (-vertices[0][1] + vertices[1][1]), (-vertices[0][1] + vertices[2][1]), 0, dynamictype]).tolist()
    elif classtype == 2:
        # 返回形状类型，左下角顶点坐标，两个长，两个宽，动态类型，标签
        return np.array([2, vertices[0][0][0], vertices[0][0][1], vertices[0][2][0] - vertices[0][0][0], vertices[2][2][0] - vertices[0][0][0], vertices[1][1][1] - vertices[0][0][1], vertices[2][1][1] - vertices[0][0][1], dynamictype]).tolist()
    elif classtype == 3:
        # 返回形状类型，中心点坐标，半径，动态类型，标签
        return np.array([3, vertices[0], vertices[1], vertices[2], 0, 0, 0, dynamictype]).tolist()
    elif classtype == 4:
        # 返回形状类型，左下角顶点坐标，高，长边宽，短边宽，动态类型，标签
        return np.array([4, vertices[0][0], vertices[0][1], (vertices[0][1] - vertices[1][1]), (vertices[0][0] - vertices[3][0]), (-vertices[1][0] + vertices[2][0]), 0, dynamictype]).tolist()

def vis_scene(file, cata):
    pgw = loadFromDict(file['world'])
    img = pg.surfarray.array3d(drawWorld(pgw)).transpose(1, 0, 2)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    cv2.imwrite(f'./detect_data/{cata}.png', img)
    original_img = cv2.imread(f"./images/Original/{cata}.png")
    if img is None or original_img is None:
        print("Failed to load one or both images. Check the file paths.")
    else:
        height1, width1 = img.shape[:2]
        height2, width2 = original_img.shape[:2]

    # 确保两张图片高度一致
    if height1 != height2:
        original_img = cv2.resize(original_img, (width2 * height1 // height2, height1))

    # 水平拼接图片
    combined_image = np.hstack((img, original_img))

    # 显示拼接后的图片
    cv2.imshow("Combined Image", combined_image)

    # 等待按键并关闭窗口
    cv2.waitKey(0)
    cv2.destroyAllWindows()