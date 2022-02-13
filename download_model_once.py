import torch
import torchvision.models as models

model = models.vgg19(pretrained=True).features[:5]
torch.save(model, 'model.pth')