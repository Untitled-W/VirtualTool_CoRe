import numpy as np
import pygame as pg
import json
import cv2
from pyGameWorld import ToolPicker
from pyGameWorld.viewer import drawWorld, loadFromDict
from reward_function import reward_func
import time

file_dir = './Trials/Original/Bridge.json'
N = 50000
reward_list = np.zeros(N, dtype=np.float32)
flag = 0
start_time = time.time()

while True:
    if flag >= N:
        np.save('./bridge.npy', reward_list)
        break
    with open(file_dir, 'r') as f:
        file = json.load(f)
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
        
        tool_choice = np.random.randint(1, 4)
        
        x = np.random.rand(1)
        y = np.random.rand(1) * 0.6
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
        
        cv2.imwrite(f'./bridge/{flag:05d}.png', img)
        flag += 1
        if flag % 50 == 0:
            print(f'{flag:05d}', f'{100 * np.sum(reward_list[:flag] == 1.0) / flag:6.2f}%', f'{100 * np.sum(np.logical_not(reward_list[:flag] == 1.0)) / flag:6.2f}%')
            print(f'Average {flag / (time.time() - start_time):.2f}img/s')
            print(f'Left {(time.time() - start_time) / flag * (50000 - flag):.2f}s')
        np.save('./bridge.npy', reward_list)
    
        if success == True:
            for i in (-24, -20, -16, -12, -8, -4, 4, 8, 12, 16, 20, 24):
                for j in (-24, -20, -16, -12, -8, -4, 4, 8, 12, 16, 20, 24):
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
                        cv2.imwrite(f'./bridge/{flag:05d}.png', img)
                        flag += 1
                        if flag % 50 == 0:
                            print(f'{flag:05d}', f'{100 * np.sum(reward_list[:flag] == 1.0) / flag:6.2f}%', f'{100 * np.sum(np.logical_not(reward_list[:flag] == 1.0)) / flag:6.2f}%')
                            print(f'Average {flag / (time.time() - start_time):.2f}img/s')
                            print(f'Left {(time.time() - start_time) / flag * (50000 - flag):.2f}s')
                        np.save('./bridge.npy', reward_list)