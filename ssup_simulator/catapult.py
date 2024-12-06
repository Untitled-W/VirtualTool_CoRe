import numpy as np
import pygame as pg
import json
import cv2
from pyGameWorld import ToolPicker
from pyGameWorld.viewer import drawWorld, loadFromDict
from reward_function import reward_func
import time

file_dir = './Trials/Original/Catapult.json'
N = 50000
reward_list = np.zeros(N, dtype=np.float32)
flag = 0
start_time = time.time()

while True:
    if flag >= N:
        np.save('./catapult.npy', reward_list)
        break
    with open(file_dir, 'r') as f:
        file = json.load(f)
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
        
        tool_choice = np.random.randint(1, 4)
        x = np.random.rand(1)
        y = np.random.rand(1)
        tp = ToolPicker(file)
        path_dict, success, time_to_success = tp.observePlacementPath(toolname=f"obj{tool_choice:d}", position=(int(600 * x), int(600 * y)), maxtime=20.)
        if success is None:
            reward_value = -1
        else:
            reward_value = reward_func(path_dict['Ball'], file['world']['objects']['Goal']['points'], 15)
        reward_list[flag] = reward_value
        
        file['world']['objects']['tool'] = {"type": "Poly", "color": "red", "density": 1, "vertices": [[content[0] + int(600 * x), content[1] + int(600 * y)] for content in file['tools'][f'obj{tool_choice:d}'][0]]}
        pgw = loadFromDict(file['world'])
        img = pg.surfarray.array3d(drawWorld(pgw)).transpose(1, 0, 2)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(f'./catapult/{flag:05d}.png', img)
        flag += 1
        if flag % 50 == 0:
            print(f'{flag:05d}', f'{100 * np.sum(reward_list[:flag] == 1.0) / flag:6.2f}%', f'{100 * np.sum(np.logical_not(reward_list[:flag] == 1.0)) / flag:6.2f}%')
            print(f'Average {flag / (time.time() - start_time):.2f}img/s')
            print(f'Left {(time.time() - start_time) / flag * (50000 - flag):.2f}s')
        np.save('./catapult.npy', reward_list)

        if success == True:
            for i in (-30, -24, -18, -12, -6, 6, 12, 18, 24, 30):
                for j in (-30, -24, -18, -12, -6, 6, 12, 18, 24, 30):
                    tmp_path_dict, tmp_success, tmp_time_to_success = tp.observePlacementPath(toolname=f"obj{tool_choice:d}", position=(int(600 * x) + i, int(600 * y) + j), maxtime=20.)
                    if tmp_success is None:
                        tmp_reward_value = -1
                    else:
                        tmp_reward_value = reward_func(tmp_path_dict['Ball'], file['world']['objects']['Goal']['points'], 15)
                    if tmp_reward_value >= 1.0:
                        reward_list[flag] = tmp_reward_value
                        file['world']['objects']['tool'] = {"type": "Poly", "color": "red", "density": 1, "vertices": [[content[0] + int(600 * x) + i, content[1] + int(600 * y) + j] for content in file['tools'][f'obj{tool_choice:d}'][0]]}
                        pgw = loadFromDict(file['world'])
                        img = pg.surfarray.array3d(drawWorld(pgw)).transpose(1, 0, 2)
                        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                        cv2.imwrite(f'./catapult/{flag:05d}.png', img)
                        flag += 1
                        if flag % 50 == 0:
                            print(f'{flag:05d}', f'{100 * np.sum(reward_list[:flag] == 1.0) / flag:6.2f}%', f'{100 * np.sum(np.logical_not(reward_list[:flag] == 1.0)) / flag:6.2f}%')
                            print(f'Average {flag / (time.time() - start_time):.2f}img/s')
                            print(f'Left {(time.time() - start_time) / flag * (50000 - flag):.2f}s')
                        np.save('./catapult.npy', reward_list)