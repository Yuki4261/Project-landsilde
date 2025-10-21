from streamlit.components.v1 import html
import folium
import requests
import config
from config import ORS_API_KEY, origin, destination, disaster_mask_path, disaster_center, height
from utils.map_utils import add_mask_to_map, mark_points
from utils.route_utils import get_route_with_mode
from utils.UNet_mask import create_mask
from utils.find_fire_station import get_nearest_fire_station
import streamlit as st
from streamlit_folium import st_folium
import os
from PIL import Image


def update_config(var_name, lat, lon):
    """更新 config.py 中的座標"""
    with open("config.py", "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open("config.py", "w", encoding="utf-8") as f:
        for line in lines:
            if line.startswith(f"{var_name}"):
                f.write(f"{var_name} = ({lat}, {lon})\n")
            else:
                f.write(line)
    st.info(f"✅ 已更新 {var_name} = ({lat:.6f}, {lon:.6f})")


def coordinate_editor(name, var_name, current_value):
    """建立一個可展開地圖的座標設定介面"""
    if f"show_{var_name}" not in st.session_state:
        st.session_state[f"show_{var_name}"] = False

    # 開關按鈕
    if st.button(f"📍 設定{name} ({var_name})"):
        st.session_state[f"show_{var_name}"] = not st.session_state[f"show_{var_name}"]

    st.write(f"目前{name}：{current_value}")

    # 如果展開地圖
    if st.session_state[f"show_{var_name}"]:
        st.write(f"請在地圖上點選{name}位置👇")
        m = folium.Map(location=current_value, zoom_start=13)
        m.add_child(folium.LatLngPopup())
        output = st_folium(m, height=450, width=700)

        # 點擊更新座標
        if output and output["last_clicked"]:
            lat = output["last_clicked"]["lat"]
            lon = output["last_clicked"]["lng"]
            st.success(f"你選擇的{name}座標：({lat:.6f}, {lon:.6f})")
            update_config(var_name, lat, lon)




def main():
    st.title("🌍 土石流救災地圖系統")

    # 模式選擇：'reroute' or 'rescue' or 'exit'
    # 建立下拉選單
    options = ["rescue(從最近的消防隊到災區)", "rescue(從目前位置到災區)", "reroute(規避災區的路線）"]
    choice = st.selectbox("請選擇導航方案：", options)

    # 顯示使用者選擇
    st.write(f"你選擇的導航方案是：**{choice}**")

    # 根據選擇顯示不同內容
    if choice == "最短距離":
        st.info("rescue(從最近的消防隊到災區)。")
    elif choice == "最少時間":
        st.info("rescue(從目前位置到災區)。")
    elif choice == "避開高速公路":
        st.info("reroute(規避災區的路線）。")

    coordinate_editor("災區位置", "disaster_center", config.disaster_center)
    st.divider()
    coordinate_editor("目的地", "destination", config.destination)
    st.divider()
    coordinate_editor("目前位置", "origin", config.origin)

    
    st.header("土石流圖片")

    st.image("data\Aerophoto.jpg", use_container_width=True)

    # 初始化 session_state（用來記錄上傳介面是否開啟）
    if "show_uploader" not in st.session_state:
        st.session_state.show_uploader = False

    # 按鈕切換顯示狀態
    if st.button("📤 開啟 / 關閉 上傳圖片"):
        st.session_state.show_uploader = not st.session_state.show_uploader

    # 如果開啟了上傳介面
    if st.session_state.show_uploader:
        st.info("請上傳圖片")

        uploaded_file = st.file_uploader("上傳圖片", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            # 顯示圖片
            image = Image.open(uploaded_file)
            st.image(image, caption="已上傳圖片預覽", use_container_width=True)

            # 儲存檔案
            save_path = os.path.join("data", "Aerophoto.jpg")
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.success(f"✅ 圖片已儲存到：{save_path}")

    # 初始化地圖
    m = folium.Map(location=origin, zoom_start=15)
    fire_station_location = (0,0)
    
    # 加上起點與終點
    if st.button(f"規劃路線)"):
        error = False
        if choice == "rescue(從最近的消防隊到災區)":
            fire_station_name, fire_station_address, fire_station_location = get_nearest_fire_station()
            if fire_station_name != "未找到最近的消防局":
                print(f"最近的消防局名稱: {fire_station_name}")
                print(f"地址: {fire_station_address}")
                print(f"座標: ({fire_station_location})")
                mark_points(m, {"消防局": fire_station_location, "災區中心": disaster_center})
            else:
                print(fire_station_name)  # 如果沒有找到，會顯示錯誤訊息
                error = True

        elif choice == "rescue(從目前位置到災區)":
            mark_points(m, {"目前位置": origin, "災區中心": disaster_center})
        elif choice == "reroute(規避災區的路線）":
            mark_points(m, {"目前位置": origin, "終點": destination, "災區中心": disaster_center})
        else:
            return
        if error == True:
            return
        # 生成遮罩
        print("生成遮罩")
        create_mask()

        # 加入遮罩圖層
        print("加入遮罩圖層")
        add_mask_to_map(m, disaster_center, height , disaster_mask_path)

        # 路徑規劃與繪製
        print("路徑規劃與繪製")
        get_route_with_mode(m, choice, origin, destination, disaster_center, fire_station_location, ORS_API_KEY)

        # 匯出地圖
        print("匯出地圖")
        m.save("output/output_map.html")
        print("地圖已儲存至 output/output_map.html")

        # ---- 顯示圖片（可使用 URL 或本地檔） ----
        st.header("空拍機圖片")

        # # 範例 2：本地圖片（若你有 local/path/to/image.jpg）
        # st.image("output\overlay_result.png", caption="土石流遮罩", use_container_width=True)
        # 建立兩個欄位（左、右）
        col1, col2 = st.columns(2)

        # 左邊放「災前」圖片
        with col1:
            st.subheader("原始圖片")
            st.image("data\Aerophoto.jpg", use_container_width=True)

        # 右邊放「災後」圖片
        with col2:
            st.subheader("土石流遮罩")
            st.image("output\overlay_result.png", use_container_width=True)


        st.markdown("---")

        # ---- 嵌入 HTML ----
        st.header("路線地圖")

        # 讀取本地 HTML 檔案
        html_path = "output\output_map.html"  
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # 在 Streamlit 中嵌入顯示
        html(html_content, height=600, scrolling=True)


if __name__ == "__main__":
    main()




