import torch
import torchvision.models as models

'''
файлик только чтобы идин раз загрузить 29 первых слоя vgg19
'''
model = models.vgg19(pretrained=True).features[:29]
torch.save(model, 'model.pth')
