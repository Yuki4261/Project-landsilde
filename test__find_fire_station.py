import requests

def get_nearest_fire_station(api_key, lat, lng):
    # Google Places API endpoint
    endpoint_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    # 設定查詢條件
    params = {
        "location": f"{lat},{lng}",
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
            lat = location["lat"]
            lng = location["lng"]
            return name, address, lat, lng
        else:
            return "未找到最近的消防局", "", None, None
    else:
        return f"API 請求失敗，錯誤碼：{response.status_code}", "", None, None

# 設定你的 Google API 金鑰
API_KEY = "AIzaSyBcT_MZbbY7aNXHSNFllIonQQRXc9yyPSc"

# 輸入座標（例如：台北市的某個位置）
latitude = 24.693891441199046
longitude = 120.88514993193111

# 呼叫函數
fire_station_name, fire_station_address, fire_station_lat, fire_station_lng = get_nearest_fire_station(API_KEY, latitude, longitude)

if fire_station_name:
    print(f"最近的消防局名稱: {fire_station_name}")
    print(f"地址: {fire_station_address}")
    print(f"座標: ({fire_station_lat}, {fire_station_lng})")
else:
    print(fire_station_name)  # 如果沒有找到，會顯示錯誤訊息
