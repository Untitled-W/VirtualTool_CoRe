import numpy as np
import pygame as pg
import json
import cv2
from pyGameWorld import ToolPicker
from pyGameWorld.viewer import drawWorld, loadFromDict
import time

file_dir = './tool-games/environment/Trials/Original/Bridge.json'
N = 50000
reward_list = np.zeros(N, dtype=np.float32)
flag = 0
start_time = time.time()

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
    
    # x = np.random.rand(1)
    # y = np.random.rand(1) * 0.6
    # tp = ToolPicker(file)
    
    
    # file['world']['objects']['tool'] = {"type": "Poly", "color": "red", "density": 1, "vertices": [[content[0] + int(600 * x), content[1] + int(600 * y)] for content in file['tools'][f'obj{tool_choice:d}'][0]]}
    pgw = loadFromDict(file['world'])
    img = pg.surfarray.array3d(drawWorld(pgw)).transpose(1, 0, 2)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    cv2.imwrite(f'./detect_data/bridge.png', img)
    
    
    original_img = cv2.imread("./images/Original/Bridge.png")
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