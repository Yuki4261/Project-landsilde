import folium
import base64
import math
from folium.plugins import FloatImage
import cv2
import numpy as np

def mask_to_red_transparent(input_path):
    mask = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)

    # 建立 RGBA 圖片（彩色 + Alpha 通道）
    rgba = np.zeros((mask.shape[0], mask.shape[1], 4), dtype=np.uint8)

    # 黑色部分（像素值 < 128）改成紅色（255,0,0），透明度 255
    black_area = mask < 128
    rgba[black_area] = [255, 0, 0, 150]

    # 白色部分（像素值 >= 128）透明
    white_area = mask >= 128
    rgba[white_area] = [0, 0, 0, 0]
    
    return rgba



def add_mask_to_map(m, disaster_center, height , image_path):
    # 直接疊加在地圖上（需要使用 bounds 定位）
    # 你可以調整 bounds 對應災區座標

    lat_per_meter = 1 / 111320
    # 1 公尺對應的經度差（需考慮緯度收縮）
    center_lat = disaster_center[0]
    # print(f"center_lat= {center_lat}")
    lon_per_meter = 1 / (111320 * math.cos(math.radians(center_lat)))
    
    # 圖片實際覆蓋距離
    gsd = (height * 12.3)/(24 * 256)

    # gsd = 6.52
    half_width_m = (256 / 2) * gsd
    half_height_m = (256 / 2) * gsd
    
    # 計算左下角與右上角座標
    lat_min = disaster_center[1] - half_height_m * lat_per_meter
    lat_max = disaster_center[1] + half_height_m * lat_per_meter
    lon_min = disaster_center[0] - half_width_m * lon_per_meter
    lon_max = disaster_center[0] + half_width_m * lon_per_meter
    
    bounds = [[lon_min, lat_min], [lon_max, lat_max]]

    # print(f"bounds = {bounds}")

    # bounds = [[24.681, 121.378], [24.686, 121.384]]  # 左下角, 右上角
    folium.raster_layers.ImageOverlay(
        name='災區遮罩',
        image=mask_to_red_transparent(image_path),
        bounds=bounds,
        opacity=0.6,
        interactive=True,
        cross_origin=False
    ).add_to(m)

def mark_points(m, points: dict):
    for label, coord in points.items():
        folium.Marker(location=coord, popup=label, icon=folium.Icon(color="red")).add_to(m)
