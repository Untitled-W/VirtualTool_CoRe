import torch, json, cv2
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from tqdm import trange, tqdm
import numpy as np
from pyGameWorld import ToolPicker
from pyGameWorld.viewer import drawWorld, loadFromDict
from reward_function import reward_func
import pygame as pg

class PolicyNet(nn.Module):
    def __init__(self):
        super(PolicyNet, self).__init__()
        self.image_features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1),  # (128, 128) -> (128, 128)
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),  # (128, 128) -> (64, 64)
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),  # (64, 64) -> (64, 64)
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),  # (64, 64) -> (32, 32)
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),  # (32, 32) -> (32, 32)
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),  # (32, 32) -> (16, 16)
            nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1),  # (16, 16) -> (16, 16)
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),  # (16, 16) -> (8, 8)
            nn.AdaptiveAvgPool2d(1)  # (8, 8) -> (256, 1, 1)
        )
        self.tool_features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, stride=3, padding=0),  # (90, 90) -> (30, 30)
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=3, padding=0),  # (30, 30) -> (10, 10)
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1)  # (10, 10) -> (64, 1, 1)
        )
        self.regressor = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256+64, 128),  # 降维
            nn.ReLU(),
            nn.Linear(128, 4),  # 回归输出单值
            nn.Sigmoid()
        )
    # 前向传播
    def forward(self, img, tool):
        x1, x2 = self.image_features(img), self.tool_features(tool)
        x = self.regressor(torch.cat([x1, x2], dim=1))
        mean, std = x[:, :2], x[:, 3:]
        x = torch.normal(mean, std)
        x = torch.clamp(x, 0, 1)
        return x, mean, std
    
class BridgeEnv:
    def __init__(self):
        file_dir = '../tool-games/environment/Trials/Original'+'/Bridge.json'
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
        
        self.file = file
        
    def get_state(self):
        pgw = loadFromDict(self.file['world'])
        img = pg.surfarray.array3d(drawWorld(pgw)).transpose(1, 0, 2)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        tool_choice = np.random.randint(1, 4)
        self.tool_choice = tool_choice
        tool_points = self.file['tools'][f'obj{tool_choice:d}'][0]
        tool_points = [[content[0]+45, content[1]+45] for content in tool_points]
        tool_image = np.zeros((90, 90, 1), dtype=np.uint8)
        cv2.fillPoly(tool_image, [np.array(tool_points)], 255)
        return img, tool_image
        
    def get_reward(self, p):
        x, y = p
        tp = ToolPicker(self.file)
        path_dict, success, time_to_success = tp.observePlacementPath(toolname=f"obj{self.tool_choice:d}", position=(int(600 * x), int(600 * y)), maxtime=20.)
        if success is None:
            return -1
        else:
            return reward_func(path_dict['Ball'], self.file['world']['objects']['Goal']['points'], 15)   
    
class CatapultEnv:
    pass    
    
class Env:
    def __init__(self, env_name, batch_size=1):
        if env_name == 'Bridge':
            self.envs = [BridgeEnv() for _ in range(batch_size)]
        elif env_name == 'Catapult':
            self.envs = [CatapultEnv() for _ in range(batch_size)]
        else:
            raise ValueError('Unknown environment name: {}'.format(env_name))
        self.batch_size = batch_size
        
    def get_state(self):
        images, tools = [], []
        for env in self.envs:
            img, tool = env.get_state()
            images.append(img)
            tools.append(tool)
        return np.stack(images), np.stack(tools)
    
    def get_reward(self, ps):
        rewards = []
        for env, p in zip(self.envs, ps):
            reward = env.get_reward(p)
            rewards.append(reward)
        return np.array(rewards)
    

    
if __name__ == '__main__':
    batch_size = 2
    env = Env('Bridge', batch_size)
    policy_model = PolicyNet().cuda()
    img, tool = env.get_state()
    img = torch.tensor(img).permute(0, 3, 1, 2).float().cuda()
    tool = torch.tensor(tool).permute(0, 3, 1, 2).float().cuda()
    actions, mean, std = policy_model(img, tool)
    rewards = env.get_reward(actions)
    rewards = torch.tensor(rewards).float().cuda()
    print(rewards.shape, actions.shape, mean.shape, std.shape)
    # policy gradient for continuous action space
    loss = (np.sqrt(2 * np.pi) * torch.log(std).sum() + 0.5 * (((actions - mean) / std) ** 2).sum()) * rewards
    print(loss.shape)