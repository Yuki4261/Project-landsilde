import torch
from PIL import Image
from torchvision import transforms
import numpy as np
import cv2
import os
import urllib.request
from utils.UNet_train import UNet  

def create_mask():
    MODEL_PATH = "utils/unet_trained.pth"
    MODEL_URL = "https://drive.google.com/uc?export=download&id=1Ojstnss2AiJ7Q8Viukt305-jMO4DRCq9"

    # 下載模型（若不存在）
    if not os.path.exists(MODEL_PATH):
        print("Downloading model...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Model downloaded successfully.")

    # 初始化模型
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = UNet().to(device)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    model.eval()

    # 載入影像
    img_path = "data/Aerophoto.jpg"
    image = Image.open(img_path).convert("RGB").resize((256, 256))

    transform = transforms.ToTensor()
    input_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(input_tensor)
        pred_mask = output.squeeze().cpu().numpy()

    # 二值化遮罩
    mask_bin = (pred_mask > 0.5).astype(np.uint8) * 255
    os.makedirs("output", exist_ok=True)
    cv2.imwrite("data/landslide_mask.png", mask_bin)

    # 疊加紅色遮罩
    image_cv = np.array(image)
    red_mask = np.zeros_like(image_cv)
    red_mask[:, :, 0] = 255
    alpha = 0.2
    overlay = image_cv.copy()
    overlay[mask_bin > 0] = cv2.addWeighted(
        image_cv[mask_bin > 0], 1 - alpha,
        red_mask[mask_bin > 0], alpha, 0
    )

    cv2.imwrite("output/overlay_result.png", overlay)
    print("已儲存為 output/overlay_result.png")
