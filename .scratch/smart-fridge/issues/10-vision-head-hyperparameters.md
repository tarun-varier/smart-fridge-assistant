Type: grilling
Status: open

## Question

Given the Vision Pipeline Architecture ticket's locked plan (frozen ResNet18, cached features, train only a new head), decide the concrete head hyperparameters: head architecture (single linear layer vs. a small MLP with a hidden layer), epochs, batch size, learning rate, and optimizer — sized for training on cached feature vectors (not raw images), so cost is dominated by the one-time feature-extraction pass, not by this step.
