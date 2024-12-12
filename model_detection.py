import torch
import torch.nn as nn
import torch.nn.functional as F

class MLP(nn.Module):
    def __init__(self, in_dim, out_dim=None, hidden_dim=None, dropout=0.1):
        super().__init__()
        if out_dim is None:
            out_dim = in_dim
        if hidden_dim is None:
            hidden_dim = 2 * in_dim

        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, out_dim)
        )

    def forward(self, x):
        return self.net(x)
    
class Attention(nn.Module):
    def __init__(self, dim, num_heads=4):
        super().__init__()
        self.dim = dim
        self.num_heads = num_heads
        assert dim % num_heads == 0, "dim must be divisible by num_heads"

        self.qkv = nn.Linear(dim, dim*3)


    def forward(self, x):
        # Step 1: Compute qkv and split into q, k, v
        qkv = self.qkv(x)
        q, k, v = qkv.chunk(3, dim=-1)
        
        # Step 2: Reshape q, k, v for multi-head attention
        B, N, D = x.size()
        assert D == self.dim
        head_dim = self.dim // self.num_heads
        
        q = q.view(B, N, self.num_heads, head_dim).transpose(1, 2)  # (B, heads, N, head_dim)
        k = k.view(B, N, self.num_heads, head_dim).transpose(1, 2)  # (B, heads, N, head_dim)
        v = v.view(B, N, self.num_heads, head_dim).transpose(1, 2)  # (B, heads, N, head_dim)
        
        # Step 3: Compute the attention scores (scaled dot-product)
        attn_scores = torch.matmul(q, k.transpose(-2, -1)) / (head_dim ** 0.5)  # (B, heads, N, N)
        
        # Step 4: Apply softmax to get attention weights
        attn_weights = torch.softmax(attn_scores, dim=-1)  # (B, heads, N, N)
        
        # Step 5: Compute the weighted sum of values
        output = torch.matmul(attn_weights, v)  # (B, heads, N, head_dim)
        
        # Step 6: Concatenate the heads and project the result back to the original dimension
        output = output.transpose(1, 2).contiguous().view(B, N, self.dim)  # (B, N, dim)
        
        return output
    
class DetectionModel(nn.Module):
    def __init__(self, dim, in_dim, num_layers=2, num_heads=4, dropout=0.1):
        super().__init__()
        
        self.dim = dim
        self.in_dim = in_dim
        self.num_layers = num_layers

        self.emb = nn.Linear(in_dim, dim)

        self.attns = nn.ModuleList([
            Attention(dim, num_heads=num_heads) for _ in range(num_layers)
        ])

        self.mlps = nn.ModuleList([
            MLP(dim, dropout=dropout) for _ in range(num_layers)
        ])

        self.norms_1 = nn.ModuleList([
            nn.LayerNorm(dim) for _ in range(num_layers)
        ])
        self.norms_2 = nn.ModuleList([
            nn.LayerNorm(dim) for _ in range(num_layers)
        ])

        self.head = MLP(in_dim=dim, out_dim=1, dropout=dropout)
        # self.activation = nn.Sigmoid()

    def forward(self, x):

        x = self.emb(x)

        for i in range(self.num_layers):
            attn, mlp, norm_1, norm_2 = self.attns[i], self.mlps[i], self.norms_1[i], self.norms_2[i]

            x = x + attn(norm_1(x))
            x = x + mlp(norm_2(x))

        logits = self.head(x)

        return logits



