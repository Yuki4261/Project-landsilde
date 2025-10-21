import folium
import requests
import config
from config import ORS_API_KEY, origin, destination, disaster_mask_path, disaster_center, height
from utils.map_utils import add_mask_to_map, mark_points
from utils.route_utils import get_route_with_mode
from utils.UNet_mask import create_mask
from utils.find_fire_station import get_nearest_fire_station

def main():
    # 模式選擇：'reroute' or 'rescue' or 'exit'
    mode = input("請輸入模式：\n1->rescue(從最近的消防隊到災區)\n2->rescue(從目前位置到災區)\n3->reroute(規避災區的路線）\nother->exit：\n").strip().lower()

    # 初始化地圖
    m = folium.Map(location=origin, zoom_start=15)
    fire_station_location = (0,0)
    
    # 加上起點與終點
    if mode == '1':
        mode = "rescue(從最近的消防隊到災區)"
        config.disaster_center = (24.91242033624247, 121.36950521628694)
        fire_station_name, fire_station_address, fire_station_location = get_nearest_fire_station()
        if fire_station_name:
            print(f"最近的消防局名稱: {fire_station_name}")
            print(f"地址: {fire_station_address}")
            print(f"座標: ({fire_station_location})")
        else:
            print(fire_station_name)  # 如果沒有找到，會顯示錯誤訊息
        mark_points(m, {"消防局": fire_station_location, "災區中心": disaster_center})

    elif mode == '2':
        mode = "rescue(從目前位置到災區)"
        mark_points(m, {"目前位置": origin, "災區中心": disaster_center})
    elif mode == '3':
        mode = "reroute(規避災區的路線）"
        mark_points(m, {"目前位置": origin, "終點": destination, "災區中心": disaster_center})
    else:
        return

    # 生成遮罩
    print("生成遮罩")
    create_mask()
    # 加入遮罩圖層
    print("加入遮罩圖層")
    add_mask_to_map(m, disaster_center, height , disaster_mask_path)
    # 路徑規劃與繪製
    print("路徑規劃與繪製")
    get_route_with_mode(m, mode, origin, destination, disaster_center, fire_station_location, ORS_API_KEY)
    # 匯出地圖
    print("匯出地圖")
    m.save("output/output_map.html")
    print("地圖已儲存至 output/output_map.html")


if __name__ == "__main__":
    main()