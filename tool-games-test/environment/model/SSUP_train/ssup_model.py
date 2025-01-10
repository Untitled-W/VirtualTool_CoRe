import torch, json, cv2, time, os
import torch.nn as nn
import torchvision.transforms as transforms
import numpy as np
from pyGameWorld import ToolPicker
from pyGameWorld.viewer import drawWorld, loadFromDict
from .reward_function import reward_func
import pygame as pg

img_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

tool_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485], std=[0.229])
])

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
        try:
            x = torch.normal(mean, std)
        except:
            raise (img, tool, x1, x2, x)
        x = torch.clamp(x, 0, 1)
        return x, mean, std
    
class BaseEnv:    
    
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
        img = img_transform(img)
        tool_image = tool_transform(tool_image)
        return img, tool_image
        
    def get_reward(self, p):
        x, y = p
        tp = ToolPicker(self.file)
        path_dict, success, time_to_success = tp.observePlacementPath(toolname=f"obj{self.tool_choice:d}", position=(int(600 * x), int(600 * y)), maxtime=20.)
        if success is None:
            return -1
        else:
            return reward_func(path_dict['Ball'], self.file['world']['objects']['Goal']['points'], 15)   
  
    def get_next(self, p):
        x, y = p
        file = self.file
        file['world']['objects']['tool'] = {"type": "Poly", "color": "red", "density": 1, "vertices": [[content[0] + int(600 * x), content[1] + int(600 * y)] for content in file['tools'][f'obj{self.tool_choice:d}'][0]]}
        pgw = loadFromDict(file['world'])
        img = pg.surfarray.array3d(drawWorld(pgw)).transpose(1, 0, 2)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        img = img_transform(img)
        return img
    
class BridgeEnv(BaseEnv):
    
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
        
class CatapultEnv(BaseEnv):
    
    def __init__(self):
        file_dir = '../tool-games/environment/Trials/Original'+'/Catapult.json'
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
        
        self.file = file
    
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
   
    def get_next(self, ps):
        next_states = []
        for env, p in zip(self.envs, ps):
           next_state = env.get_next(p)
           next_states.append(next_state)
        return np.stack(next_states)
    
class Logger:
    def __init__(self, file_path=''):
        if file_path == '':
            file_path = time.strftime('%m-%d-%H-%M-%S', time.localtime()) + '.json'
        self.file_path = os.path.join('logs',file_path)
    def write(self, content):
        with open(self.file_path, 'a') as fp:
            json.dump(content, fp, indent=4)
    
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
    loss = (np.sqrt(2 * np.pi) * torch.log(std).sum() + 0.5 * (((actions - mean) / std) ** 2).sum()) * rewards