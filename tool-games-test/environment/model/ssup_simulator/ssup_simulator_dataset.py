from torch.utils.data import Dataset
class ImageRewardDataset(Dataset):
    def __init__(self, images, rewards, transform=None):
        self.images = images
        self.rewards = rewards
        self.transform = transform
    def __len__(self):
        return len(self.rewards)
    def __getitem__(self, idx):
        image = self.images[idx]
        reward = self.rewards[idx]
        if self.transform:
            image = self.transform(image)
        return image, reward