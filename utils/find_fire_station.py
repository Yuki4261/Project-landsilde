import requests
import config 


def get_nearest_fire_station():
    # 設定你的 Google API 金鑰
    api_key = "AIzaSyBcT_MZbbY7aNXHSNFllIonQQRXc9yyPSc"
    # Google Places API endpoint
    endpoint_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    # 設定查詢條件
    lat, lon = config.disaster_center
    print(f"災區座標：{config.disaster_center}")
    params = {
        "location": f"{lat},{lon}",
        "radius": 5000,  # 搜尋半徑，單位為米（這裡設為5000米）
        "type": "fire_station",  # 查找消防局
        "key": api_key
    }
    
    # 發送請求到 Google Places API
    response = requests.get(endpoint_url, params=params)
    
    # 確認回應是否成功
    if response.status_code == 200:
        results = response.json().get("results", [])
        
        # 如果找到了消防局
        if results:
            nearest_station = results[0]
            name = nearest_station["name"]
            address = nearest_station.get("vicinity", "無法取得地址")
            location = nearest_station["geometry"]["location"]
            location = (location["lat"],location["lng"])
            # lng = location["lng"]
            return name, address, location
        else:
            return "未找到最近的消防局", "", None
    else:
        return f"API 請求失敗，錯誤碼：{response.status_code}", "", None




