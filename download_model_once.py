import torch
import torchvision.models as models

'''
файлик только чтобы идин раз загрузить 3 первых слоя vgg19
'''
model = models.vgg19(pretrained=True).features[:2]
torch.save(model, 'model.pth')
