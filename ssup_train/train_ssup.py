import sys
sys.path.append('.')

import os
os.environ['CUDA_VISIBLE_DEVICES'] = '3'

import torch
import torch.optim as optim
import numpy as np
from ssup_simulator import RewardCNN
from ssup_model import PolicyNet, Env, Logger
from tqdm import trange, tqdm
import cv2


NID = 0

ckpt_save_dir = './bridge_ckpt'
# ckpt_save_dir = './catapult_ckpt'


value_model = RewardCNN().cuda()
policy_model = PolicyNet().cuda()

value_model.load_state_dict(torch.load(os.path.join(ckpt_save_dir, '50.pth')))
value_model.eval()
policy_model.train()

optimizer = optim.Adam(policy_model.parameters(), lr=1e-4)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=60, gamma=0.9)

N = 1000
batch_size = 32

writer = Logger()

for i in trange(N):
    env = Env('Bridge', batch_size)
    # env = Env('Catapult', batch_size)
    img, tool = env.get_state()
    img = torch.tensor(img).float().cuda()
    tool = torch.tensor(tool).float().cuda()
    actions, mean, std = policy_model(img, tool)
    rewards = env.get_reward(actions)
    rewards = torch.tensor(rewards).float().cuda()
    next_state = env.get_next(actions)
    next_state = torch.tensor(next_state).float().cuda()
    q = value_model(next_state)
    optimizer.zero_grad()
    loss = -torch.mean((np.sqrt(2 * np.pi) * torch.log(std).sum() + 0.5 * (((actions - mean) / std) ** 2).sum()) * (rewards - q))
    loss.backward()
    
    aver_grad = {}
    aver_param = {}
    for name, param in policy_model.named_parameters():
        aver_grad[name] = param.grad.norm().item()
        aver_param[name] = param.norm().item()
    
    optimizer.step()
    
    success_rate = (rewards > -1).float().mean().item()
    
    writer.write({'Epoch': i, 'Loss': loss.item(), 'Success rate': success_rate, 'Mean reward': rewards.mean().item(), 'Std reward': rewards.std().item(), 'Grad norm': aver_grad, 'Param norm': aver_param})
    
    if i % 200 == 199:
        torch.save(policy_model.state_dict(), os.path.join(ckpt_save_dir, f'policy_{i}_{NID}.pth'))