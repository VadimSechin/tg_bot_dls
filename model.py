import torch
import torchvision.transforms as transforms
from PIL import Image
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm
from config import is_processing


def return_image(original_image, style_image_path, bot, id):
    is_processing.change(True)
    print('is processing: ', is_processing)

    device = 'cpu'

    def image_loader(image):
        image = Image.fromarray(image, "RGB")
        loader = transforms.Compose([transforms.Resize((256, 256)), transforms.ToTensor()])
        image = loader(image).unsqueeze(0)
        return image.to(device, torch.float)

    original_image = image_loader(original_image)
    style_image = image_loader(style_image_path)
    generated_image = original_image.clone().requires_grad_(True)

    class VGG(nn.Module):
        def __init__(self):
            super(VGG, self).__init__()
            self.req_features = ['5', '12', '21', '27']
            self.model = torch.load('model.pth')

        def forward(self, x):
            features = []
            for layer_num, layer in enumerate(self.model):
                x = layer(x)
                if (str(layer_num) in self.req_features):
                    features.append(x)

            return features

    def calc_content_loss(gen_feat, orig_feat):
        content_l = torch.mean((gen_feat - orig_feat) ** 2)
        return content_l

    def calc_style_loss(gen, style):
        batch_size, channel, height, width = gen.shape
        G = torch.mm(gen.view(channel, height * width), gen.view(channel, height * width).t())
        A = torch.mm(style.view(channel, height * width), style.view(channel, height * width).t())
        style_l = torch.mean((G - A) ** 2)
        return style_l

    def calculate_loss(gen_features, orig_features, style_features):
        style_loss = content_loss = 0
        for gen, cont, style in zip(gen_features, orig_features, style_features):
            content_loss += calc_content_loss(gen, cont)
            style_loss += calc_style_loss(gen, style)

        total_loss = alpha * content_loss + beta * style_loss
        return total_loss

    model = VGG().to(device).eval()

    epoch = 150
    lr = 0.005
    alpha = 8
    beta = 7000

    optimizer = optim.Adam([generated_image], lr=lr)
    for e in tqdm(range(epoch)):
        gen_features = model(generated_image)
        orig_features = model(original_image)
        style_features = model(style_image)

        total_loss = calculate_loss(gen_features, orig_features, style_features)
        optimizer.zero_grad()
        total_loss.backward()
        optimizer.step()
        if e % (epoch // 10) == 0:
            bot.send_message(id, "????????????: " + str(e // (epoch // 10) * 10) + " %")

    return generated_image
