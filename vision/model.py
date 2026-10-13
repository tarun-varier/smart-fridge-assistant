"""Vision Pipeline classification head (issue #11: Vision head hyperparameters).

Trained on cached frozen-ResNet18 feature vectors, not raw images.
"""

import torch.nn as nn


class VisionHead(nn.Module):
    def __init__(self, in_features: int = 512, hidden: int = 256, num_classes: int = 6):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_features, hidden),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden, num_classes),
        )

    def forward(self, x):
        return self.net(x)
