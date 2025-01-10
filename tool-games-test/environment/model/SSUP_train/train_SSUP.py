import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
import numpy as np
from ssup_simulator import RewardCNN
from ssup_model import PolicyNet, Env
from tqdm import trange, tqdm
import cv2
import os
from torch.utils.tensorboard import SummaryWriter

print(torch.cuda.is_available())

ckpt_save_dir = './bridge_ckpt'

value_model = RewardCNN().cuda()
policy_model = PolicyNet().cuda()

value_model.load_state_dict(torch.load(os.path.join(ckpt_save_dir, '50.pth')))
value_model.eval()
policy_model.train()

optimizer = optim.Adam(policy_model.parameters(), lr=0.001)

N = 1000
batch_size = 16

writer = SummaryWriter(log_dir='./logs')

for i in trange(N):
    env = Env('Bridge', batch_size)
    img, tool = env.get_state()
    img = torch.tensor(img).permute(0, 3, 1, 2).float().cuda()
    tool = torch.tensor(tool).permute(0, 3, 1, 2).float().cuda()
    actions, mean, std = policy_model(img, tool)
    rewards = env.get_reward(actions)
    rewards = torch.tensor(rewards).float().cuda()
    optimizer.zero_grad()
    # policy gradient for continuous action space
    loss = -torch.mean((np.sqrt(2 * np.pi) * torch.log(std).sum() + 0.5 * (((actions - mean) / std) ** 2).sum()) * rewards)
    loss.backward()
    optimizer.step()
    
    success_rate = (rewards > -1).float().mean().item()
    
    # Log the loss to Tensorboard
    writer.add_scalar('Loss/train', loss.item(), i)
    writer.add_scalar('Reward/mean', rewards.mean().item(), i)
    writer.add_scalar('Reward/std', rewards.std().item(), i)
    writer.add_scalar('Success_rate', success_rate, i)
    
    if i % 200 == 199:
        torch.save(policy_model.state_dict(), os.path.join(ckpt_save_dir, f'policy_{i}.pth'))

writer.close()