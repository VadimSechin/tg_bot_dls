import torch
import torchvision.models as models

model = models.vgg19(pretrained=True).features[:3]
torch.save(model, 'model.pth')