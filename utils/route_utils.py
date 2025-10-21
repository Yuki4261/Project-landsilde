import openrouteservice
import folium
import pyproj
from shapely.ops import transform
from shapely.geometry import Point
from shapely.geometry import mapping

# ✅ 自定函式：建立圓形避開區域
def build_avoid_polygon(center, radius=100, num_points=36):
    """
    建立一個圓形的 GeoJSON Polygon 用於 ORS 的 avoid_polygons 參數
    center: (lon, lat)
    radius: 半徑（公尺）
    """
    # 建立投影系統（從 WGS84 到米為單位）
    proj_wgs84 = pyproj.CRS('EPSG:4326')
    proj_aeqd = pyproj.Proj(proj='aeqd', lat_0=center[0], lon_0=center[1])
    project = pyproj.Transformer.from_proj(proj_wgs84, proj_aeqd, always_xy=True).transform
    project_back = pyproj.Transformer.from_proj(proj_aeqd, proj_wgs84, always_xy=True).transform

    point_transformed = transform(project, Point(center[1],center[0]))
    buffer = point_transformed.buffer(radius, resolution=num_points)
    buffer_wgs84 = transform(project_back, buffer)

    return mapping(buffer_wgs84)

def get_route_with_mode(m, mode, origin, destination, avoid_point, fire_station_location, api_key):
    client = openrouteservice.Client(key=api_key)

    radius_m = 50  # 避開半徑
    print("1")
    folium.Circle(
        location=(avoid_point),
        radius=radius_m,
        popup="危險區域",
        color='crimson',
        fill=True,
        fill_opacity=0.2
    ).add_to(m)
    print("2")
    if mode == "rescue(從最近的消防隊到災區)":     # 從最近的消防隊到災區
        route = client.directions(
            coordinates=[(fire_station_location[1], fire_station_location[0]), (avoid_point[1], avoid_point[0])],
            profile='driving-car',
            format='geojson'
        )
    elif mode == "rescue(從目前位置到災區)":   # 從目前位置到災區
        route = client.directions(
            coordinates=[(origin[1], origin[0]), (avoid_point[1], avoid_point[0])],
            profile='driving-car',
            format='geojson'
        )
    elif mode == "reroute(規避災區的路線）":   # 規避災區的路線
        # 創建避開區域 polygon (大約繞一圈災區)
        avoid_geojson = build_avoid_polygon(avoid_point, radius=radius_m)

        route = client.directions(
            coordinates=[(origin[1], origin[0]), (destination[1], destination[0])],
            profile='driving-car',
            format='geojson',
            options={
                "avoid_polygons": avoid_geojson
            }
        )
    print("3")
    folium.GeoJson(route, name="route").add_to(m)
