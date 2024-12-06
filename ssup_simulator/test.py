import torch
import numpy as np
import pygame as pg
import json
import cv2
from pyGameWorld import ToolPicker
from pyGameWorld.viewer import drawWorld, loadFromDict
from ssup_simulator import RewardCNN
from tqdm import trange

model_ckpt = './bridge_ckpt/bridge_50.pth'
scene_json = './Trials/Original/Bridge.json'
tool_choice = 1
N_sample = 5000
top_k = False
k = 1

model = RewardCNN().cuda()
model.load_state_dict(torch.load(model_ckpt))
model.eval()

file_dir = scene_json

with open(file_dir, 'r') as f:
    file = json.load(f)
    
    pgw = loadFromDict(file['world'])
    image = pg.surfarray.array3d(drawWorld(pgw)).transpose(1, 0, 2)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    tp = ToolPicker(file)
    
    reward_list = np.zeros(N_sample, dtype=np.float32)
    
    position_list = []
    
    for i in trange(N_sample, leave=False, ncols=80, unit='sample'):
        x = np.random.rand(1)
        y = np.random.rand(1)
        file['world']['objects']['tool'] = {"type": "Poly", "color": "red", "density": 1, "vertices": [[content[0] + int(600 * x), content[1] + int(600 * y)] for content in file['tools'][f'obj{tool_choice:d}'][0]]}
        pgw = loadFromDict(file['world'])
        img = pg.surfarray.array3d(drawWorld(pgw)).transpose(1, 0, 2)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        img = cv2.resize(img, (128, 128), interpolation=cv2.INTER_LINEAR)
        img = img.astype(np.float32) / 255.0
        img = torch.from_numpy(img).unsqueeze(0)
        img = img.permute(0, 3, 1, 2).cuda()
        with torch.no_grad():
            reward = model(img)
        reward_list[i] = reward.cpu().item()
        position_list.append((int(600 * x), int(600 * y)))
        if not top_k:
            cv2.circle(image, center=(int(600 * x), 599 - int(600 * y)), radius=4, color=(0, int(((np.clip(reward.cpu().item(), -1, 1) + 1) * 0.5) ** 2 * 255), int(((-np.clip(reward.cpu().item(), -1, 1) + 1) * 0.5) ** 2 * 255)), thickness=-1)
    if not top_k:
        cv2.imwrite('./vis_catapult.png', image)
    else:
        index = np.argsort(-reward_list)[:k]
        for idx in index:
            cv2.circle(image, center=(position_list[idx][0], 599 - position_list[idx][1]), radius=4, color=(0, int(((np.clip(reward_list[idx], -1, 1) + 1) * 0.5) ** 2 * 255), int(((-np.clip(reward_list[idx], -1, 1) + 1) * 0.5) ** 2 * 255)), thickness=-1)
        cv2.imwrite('./max_catapult.png', image)