import openrouteservice
import folium
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from shapely.geometry import mapping
from shapely.ops import transform
import pyproj
import json

# ✅ 自定函式：建立圓形避開區域
def build_avoid_polygon(center, radius=100, num_points=36):
    """
    建立一個圓形的 GeoJSON Polygon 用於 ORS 的 avoid_polygons 參數
    center: (lon, lat)
    radius: 半徑（公尺）
    """
    # 建立投影系統（從 WGS84 到米為單位）
    proj_wgs84 = pyproj.CRS('EPSG:4326')
    proj_aeqd = pyproj.Proj(proj='aeqd', lat_0=center[1], lon_0=center[0])
    project = pyproj.Transformer.from_proj(proj_wgs84, proj_aeqd, always_xy=True).transform
    project_back = pyproj.Transformer.from_proj(proj_aeqd, proj_wgs84, always_xy=True).transform

    point_transformed = transform(project, Point(center))
    buffer = point_transformed.buffer(radius, resolution=num_points)
    buffer_wgs84 = transform(project_back, buffer)

    return mapping(buffer_wgs84)

# ✅ ORS API 金鑰
client = openrouteservice.Client(key='eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjY1ZTQxNTY5ZmM0ZDQ0YzliMDg2ZmRkOTI5ZDJiNjZiIiwiaCI6Im11cm11cjY0In0=')  # ← 替換成你自己的

# ✅ 地點資訊
# origin = (121.37862772589801, 24.689849390033665)       # 經度, 緯度
# destination = (121.38342503776987, 24.678395547101974)  # 經度, 緯度
# avoid_point = (121.38092431127997, 24.683542950915882)  # 經度, 緯度
# radius_m = 100  # 避開半徑
origin = (121.38385232350439,24.678457407633573)       # 經度, 緯度
destination = (121.37007546707262,24.6773410460777)  # 經度, 緯度
avoid_point = (121.23544812102658,24.955587022814584)  # 經度, 緯度
radius_m = 50  # 避開半徑

# ✅ 建立 avoid_polygons GeoJSON
avoid_geojson = build_avoid_polygon(avoid_point, radius=radius_m)

# ✅ 發送 directions 請求（開車）
route = client.directions(
    coordinates=[origin, destination],
    profile='driving-car',
    format='geojson',
    # options={
    #     "avoid_polygons": avoid_geojson
    # }
)


# ✅ Folium 地圖繪製
m = folium.Map(location=[(origin[1] + destination[1]) / 2, (origin[0] + destination[0]) / 2], zoom_start=15)

# 畫出路線
folium.GeoJson(route, name='route').add_to(m)

# 起點 A
folium.Marker(location=(origin[1], origin[0]), popup="起點 A", icon=folium.Icon(color='green')).add_to(m)

# 終點 B
folium.Marker(location=(destination[1], destination[0]), popup="終點 B", icon=folium.Icon(color='red')).add_to(m)

# 避開區域 C 點（紅圈）
folium.Circle(
    location=(avoid_point[1], avoid_point[0]),
    radius=radius_m,
    popup="避開點 C",
    color='crimson',
    fill=True,
    fill_opacity=0.4
).add_to(m)

m.save("ors_route_avoid.html")
print("✅ 地圖已儲存為 ors_route_avoid.html")
