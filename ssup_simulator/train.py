import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
import numpy as np
from ssup_simulator_dataset import ImageRewardDataset
from ssup_simulator import RewardCNN
from tqdm import trange, tqdm
import cv2
import os

num_epochs = 50
image_file = './catapult'
reward_file = './catapult.npy'
ckpt_save_dir = './catapult_ckpt'

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

images = []
for i in trange(50000):
    filename = os.path.join(image_file, f'{i:05d}.png')
    img = cv2.imread(filename)
    img = cv2.resize(img, dsize=(128, 128), interpolation=cv2.INTER_LINEAR)
    img = img.astype(np.float32) / 255.0
    images.append(img)
images = np.stack(images)

rewards = np.load(reward_file)

train_indices = np.random.choice(50000, 45000, replace=False)
train_mask = np.zeros(50000, dtype=bool)
train_mask[train_indices] = True
test_mask = np.logical_not(train_mask)

images_train = images[train_mask]
images_test = images[test_mask]
rewards_train = rewards[train_mask]
rewards_test = rewards[test_mask]

train_dataset = ImageRewardDataset(images_train, rewards_train, transform=transform)
train_dataloader = DataLoader(train_dataset, batch_size=256, shuffle=True)

test_dataset = ImageRewardDataset(images_test, rewards_test, transform=transform)
test_dataloader = DataLoader(test_dataset, batch_size=256, shuffle=False)

model = RewardCNN().cuda()
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=50, eta_min=0.00001)

for epoch in range(num_epochs):
    model.train()
    epoch_train_loss = 0.0
    epoch_test_loss = 0.0
    with tqdm(train_dataloader, ncols=80, unit='batch', leave=False) as pbar:
        for images_batch, rewards_batch in train_dataloader:

            images_batch = images_batch.cuda()
            rewards_batch = rewards_batch.view(-1, 1).cuda()

            optimizer.zero_grad()
            outputs = model(images_batch)
            loss = criterion(outputs, rewards_batch)
            loss.backward()
            optimizer.step()

            epoch_train_loss += loss.item()
            pbar.set_postfix({'LOSS': f'{loss.item():.5f}'})
            pbar.update(1)
        pbar.close()
    with torch.no_grad():
        with tqdm(test_dataloader, ncols=80, unit='batch', leave=False) as pbar:
            for images_batch, rewards_batch in test_dataloader:
                images_batch = images_batch.cuda()
                rewards_batch = rewards_batch.view(-1, 1).cuda()
                outputs = model(images_batch)
                loss = criterion(outputs, rewards_batch)
                epoch_test_loss += loss.item()
                pbar.set_postfix({'LOSS': f'{loss.item():.5f}'})
                pbar.update(1)
            pbar.close()
    scheduler.step()
    torch.save(model.state_dict(), os.path.join(ckpt_save_dir, f'{epoch + 1:02d}.pth'))
    print(f"Epoch [{epoch+1}/{num_epochs}], Train_Loss: {epoch_train_loss/len(train_dataloader):.4f}, Test_Loss: {epoch_test_loss/len(test_dataloader):.4f}")
