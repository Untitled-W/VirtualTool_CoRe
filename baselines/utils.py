import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import pygame as pg
import cv2
from pyGameWorld import PGWorld
from pyGameWorld.viewer import drawWorld, drawTool

def screen_img(pgw:PGWorld):
    img = pg.surfarray.array3d(drawWorld(pgw))
    img = cv2.resize(img, (90, 90)).transpose(1, 0, 2)
    return img

def tool_img(tool:list):
    img = drawTool(tool)
    img = cv2.resize(img, (30, 30)).transpose(1, 0, 2)
    return img

class ToolImageNetwork(nn.Module):
    def __init__(self):
        super(ToolImageNetwork, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=12, kernel_size=3)
        self.conv2 = nn.Conv2d(in_channels=12, out_channels=24, kernel_size=4, stride=2)
        self.conv3 = nn.Conv2d(in_channels=24, out_channels=12, kernel_size=3)
        self.conv4 = nn.Conv2d(in_channels=12, out_channels=3, kernel_size=2)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = self.conv4(x)
        x = x.view(x.size(0), -1)
        return x

class ScreenImageNetwork(nn.Module):
    def __init__(self):
        super(ScreenImageNetwork, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=32, kernel_size=8, stride=4)
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=4, stride=2)
        self.conv3 = nn.Conv2d(in_channels=64, out_channels=32, kernel_size=3)
        self.conv4 = nn.Conv2d(in_channels=32, out_channels=16, kernel_size=2)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = self.conv4(x)
        x = x.view(x.size(0), -1)
        return x

class ToolPolicyNetwork(nn.Module):
    def __init__(self):
        super(ToolPolicyNetwork, self).__init__()
        self.fc1 = nn.Linear(300 * 3 + 576, 100)
        self.fc2 = nn.Linear(100, 3)
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

class PositionPolicyNetwork(nn.Module):
    def __init__(self):
        super(PositionPolicyNetwork, self).__init__()
        self.fc1 = nn.Linear(300 * 3 + 576, 100)
        self.fc2 = nn.Linear(100, 400)
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

def reward_function(path_dict, goal_verts):
    ball_path = path_dict['Ball']
    ball_path = np.array(ball_path)
    distance = np.zeros((ball_path.shape[0], 4), dtype=np.float32)
    x_min = goal_verts[0][0]
    x_max = goal_verts[0][0]
    y_min = goal_verts[0][1]
    y_max = goal_verts[0][1]
    for i in range(4):
        x_min = x_min if x_min < goal_verts[i][0] else goal_verts[i][0]
        x_max = x_max if x_max > goal_verts[i][0] else goal_verts[i][0]
        y_min = y_min if y_min < goal_verts[i][1] else goal_verts[i][1]
        y_max = y_max if y_max > goal_verts[i][1] else goal_verts[i][1]
        distance[:, i] = np.sqrt((ball_path[:, 0] - goal_verts[i][0]) ** 2 + (ball_path[:, 1] - goal_verts[i][1]) ** 2)
    distance = np.min(distance, axis=1)
    mask = np.logical_and(np.logical_and(ball_path[:, 0] > x_min, ball_path[:, 0] < x_max), np.logical_and(ball_path[:, 1] > y_min, ball_path[:, 1] < y_max))
    distance[mask] *= -1
    orig_distance = distance[0]
    reward = 1 - np.min(distance) / orig_distance
    return reward

if __name__ == "__main__":
    # Test
    tool_model = ToolImageNetwork()
    screen_model = ScreenImageNetwork()
    position_model = PositionPolicyNetwork()
    choice_model = ToolPolicyNetwork()

    tool_1 = torch.randn((32, 3, 30, 30))
    tool_2 = torch.randn((32, 3, 30, 30))
    tool_3 = torch.randn((32, 3, 30, 30))
    screen = torch.randn((32, 3, 90, 90))

    tool_1 = tool_model(tool_1)
    tool_2 = tool_model(tool_2)
    tool_3 = tool_model(tool_3)
    screen = screen_model(screen)

    print(tool_1.shape, tool_2.shape, tool_3.shape, screen.shape)

    fused_repre = torch.concatenate([tool_1, tool_2, tool_3, screen], dim=-1)

    position_logit = position_model(fused_repre)
    choice_logit = choice_model(fused_repre)

    print(position_logit.shape, choice_logit.shape)

    position_pred = torch.argmax(position_logit, dim=-1)
    choice_pred = torch.argmax(choice_logit, dim=-1)

    print(position_pred, choice_pred)