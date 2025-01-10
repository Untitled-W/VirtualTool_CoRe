import json
import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import Dataset, DataLoader

from .model_detection import DetectionModel
# Specify the path to your JSON file


class DetectionDataset(Dataset):
    def __init__(self, name, file_path):

        self.name = name

        # Read the JSON file and parse it as a dictionary
        with open(file_path, 'r') as file:
            data = json.load(file)

        self.num_obj = len(data[0]['objects'])
        self.in_dim = len(data[0]['objects'][0]['item'])

        self.items = [] # (N, num_obj, in_dim)
        self.labels = []
        self.objects = []

        for i, scene in enumerate(data):
            objs = scene['objects']
            items = [obj['item'] for obj in objs]
            labels = [obj['label'] for obj in objs]
            objects = [obj['object'] for obj in objs]

            self.items.append(items)
            self.labels.append(labels)
            self.objects.append(objects)

        self.upper = torch.tensor([4., 600., 600., 600.,  600., 200., 0., 1.]).float()
        self.lower = torch.tensor([0.,   0.,   0.,   0., 0.,   0., 0., 0.]).float()


    def __getitem__(self, idx):
        x = torch.tensor(self.items[idx]).float()

        x = (x - self.lower.unsqueeze(0)) / (self.upper - self.lower + 1e-6).unsqueeze(0)

        y = torch.tensor(self.labels[idx]).long()
        
        z = self.objects[idx]

        return x, y, z

    def __len__(self):
        return len(self.labels)


# Define the training loop
def train(model, train_loader, optimizer, loss_fn, device):
    model.train()
    running_loss = 0.0
    for i, (x, y, z) in enumerate(train_loader):
        x, y = x.to(device), y.to(device)

        # Zero the gradients
        optimizer.zero_grad()

        # Forward pass
        pred = model(x)

        # Compute the loss
        loss = loss_fn(pred.squeeze(), y.float())  # Squeeze to remove the extra dimension added by sigmoid
        running_loss += loss.item()

        # Backward pass and optimize
        loss.backward()
        optimizer.step()

    avg_loss = running_loss / len(train_loader)
    return avg_loss

def calculate_metrics(y_pred, y):
    y_pred, y = y_pred.long(), y.long()
    tp = ((y_pred == 1) & (y == 1)).float().sum(dim=-1)
    tn = ((y_pred == 0) & (y == 0)).float().sum(dim=-1)
    fp = ((y_pred == 1) & (y == 0)).float().sum(dim=-1)
    fn = ((y_pred == 0) & (y == 1)).float().sum(dim=-1)

    acc = (tp + tn) / (tp + tn + fp + fn)
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    return acc, precision, recall



# Define the evaluation loop
def evaluate(model, val_loader, loss_fn, device):
    model.eval()
    running_loss, running_acc, running_precision, running_recall = 0.0, 0.0, 0.0, 0.0
    total = 0

    error_mask = None

    with torch.no_grad():
        for x, y, z in val_loader:
            x, y = x.to(device), y.to(device)

            # Forward pass
            logits = model(x).squeeze()
            logits = torch.clamp(logits, -10., 10.)

            # Compute the loss
            loss = loss_fn(logits, y.float())  # Squeeze to remove the extra dimension
            running_loss += loss.item() * y.size(0)

            # Compute accuracy
            pred_label = (logits > 0).long()  # Apply Sigmoid and round to 0 or 1
            acc, precision, recall = calculate_metrics(pred_label, y)
            running_acc += acc.sum()
            running_precision += precision.sum()
            running_recall += recall.sum()
            total += y.size(0)

            if error_mask is None:
                error_mask = (pred_label != y).sum(dim=0)
            else:
                error_mask += (pred_label != y).sum(dim=0)


    avg_loss = running_loss / total
    accuracy = running_acc / total * 100.
    precision = running_precision / total * 100.
    recall = running_recall / total * 100.
    print(error_mask)
    return avg_loss, accuracy, precision, recall

if __name__ == "__main__":

    file_path = '/home/guchenyang/Codes/tool-games/environment/Trials/Generated/Compositional/bridge_data.json'
    dataset = DetectionDataset(name='bridge', file_path=file_path)

    train_size = int(0.9 * len(dataset))
    val_size = len(dataset) - train_size

    # Split the dataset into train and validation sets
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, drop_last=True)
    val_loader = DataLoader(val_dataset, batch_size=8, drop_last=False)


    # Training configuration
    device = 'cuda'  # Or use 'cuda' if you have a GPU
    model = DetectionModel(dim=256, in_dim=dataset.in_dim, num_layers=6, num_heads=4, dropout=0.2).to(device)

    def init_weights(m):
        if isinstance(m, nn.Linear):
            nn.init.xavier_uniform_(m.weight)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)

    model.apply(init_weights)

    optimizer = torch.optim.Adam(model.parameters(), lr=0.000005)
    loss_fn = nn.BCEWithLogitsLoss()  # For binary classification (or use CrossEntropyLoss for multi-class)

    # Training loop
    num_epochs = 25
    for epoch in range(num_epochs):
        train_loss = train(model, train_loader, optimizer, loss_fn, device)
        val_loss, val_acc, val_precision, val_recall = evaluate(model, val_loader, loss_fn, device)

        print(f"Epoch {epoch + 1} / {num_epochs}")
        print(f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val Accuracy: {val_acc:.2f}% | Val Precision: {val_precision:.2f}% | Val Recall: {val_recall:.2f}%")

    torch.save(model.state_dict(), './bridge_detector_1.pth')