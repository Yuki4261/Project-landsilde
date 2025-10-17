import torch
from PIL import Image
from torchvision import transforms
import numpy as np
import cv2
import matplotlib.pyplot as plt

from UNet_train import UNet  # 請確認 UNet 定義正確

# ----- 載入模型 -----
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = UNet().to(device)
model.load_state_dict(torch.load("unet_trained.pth", map_location=device))
model.eval()

# ----- 載入圖片 -----
img_path = "test.jpg"  # 測試圖片
image_pil = Image.open(img_path).convert("RGB").resize((256, 256))

# ----- 預處理 -----
transform = transforms.ToTensor()
input_tensor = transform(image_pil).unsqueeze(0).to(device)  # [1, 3, 256, 256]

# ----- 預測 -----
with torch.no_grad():
    output = model(input_tensor)  # [1, 1, H, W]
    pred_mask = output.squeeze().cpu().numpy()  # [H, W]

# ----- 閾值處理，轉成 binary mask -----
mask_bin = (pred_mask > 0.5).astype(np.uint8)

# ----- 疊加紅色半透明遮罩 -----
# 將 PIL 圖片轉為 OpenCV 格式（uint8）
image_cv = np.array(image_pil)  # [H, W, 3], uint8
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

# ----- 顯示 -----
plt.imshow(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
plt.title("紅色半透明遮罩")
plt.axis("off")
plt.show()

# ----- 儲存圖片 -----
cv2.imwrite("overlay_result.png", overlay)
print("已儲存為 overlay_result.png")
