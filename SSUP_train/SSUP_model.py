import torch
import torch.nn as nn
import torch.nn.functional as F

class PolicyNet(nn.Module):
    def __init__(self):
        super(PolicyNet, self).__init__()
        self.features = nn.Sequential(
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
        self.regressor = nn.Sequential(
            nn.Flatten(),  # 将 (256, 1, 1) 展平为 (256)
            nn.Linear(256, 128),  # 降维
            nn.ReLU(),
            nn.Linear(128, 3),  # 回归输出单值
            nn.Sigmoid()
        )
    # 前向传播
    def forward(self, x):
        x = self.features(x)
        x = self.regressor(x)
        x = torch.normal(mean=x[:, :2], std=x[:, 2].unsqueeze(1))
        x = torch.clamp(x, 0, 1)
        return x