import torch
from PIL import Image
from torchvision import transforms
import matplotlib.pyplot as plt
import numpy as np
import cv2

from utils.UNet_train import UNet  

def create_mask():

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = UNet().to(device)
    model.load_state_dict(torch.load("utils/unet_trained.pth", map_location=device))
    model.eval()

    # 載入圖片
    img_path = "data/Aerophoto.jpg"
    image = Image.open(img_path).convert("RGB").resize((256, 256))

    # 轉成 tensor
    transform = transforms.ToTensor()
    input_tensor = transform(image).unsqueeze(0).to(device)  # [1, 3, H, W]


    with torch.no_grad():
        output = model(input_tensor)  # [1, 1, H, W]
        pred_mask = output.squeeze().cpu().numpy()  # 去掉 batch 和 channel 維度


    # 將遮罩轉為 0/1（或 0~255）
    mask_bin = (pred_mask > 0.5).astype(np.uint8) * 255

    # 儲存遮罩圖
    cv2.imwrite("data/landslide_mask.png", mask_bin)


    # ----- 疊加紅色半透明遮罩 -----
    # 將 PIL 圖片轉為 OpenCV 格式（uint8）
    image_cv = np.array(image)  # [H, W, 3], uint8
    red_mask = np.zeros_like(image_cv)
    red_mask[:, :, 0] = 255  # 紅色通道

    # 混合遮罩區域
    alpha = 0.2  # 透明度 0~1
    overlay = image_cv.copy()
    overlay[mask_bin == 0] = cv2.addWeighted(
        image_cv[mask_bin == 0], 1 - alpha,
        red_mask[mask_bin == 0], alpha,
        0
    )

    # # ----- 顯示 -----
    # plt.imshow(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
    # plt.title("紅色半透明遮罩")
    # plt.axis("off")
    # plt.show()

    # ----- 儲存圖片 -----
    cv2.imwrite("output/overlay_result.png", overlay)
    print("已儲存為 overlay_result.png")