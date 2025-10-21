# import streamlit as st
# import os
# from PIL import Image

# st.header("土石流圖片上傳與儲存")

# # 上傳圖片
# uploaded_file = st.file_uploader("請上傳一張圖片", type=["jpg", "jpeg", "png"])

# if uploaded_file is not None:
#     # 顯示預覽
#     image = Image.open(uploaded_file)
#     st.image(image, caption="已上傳圖片預覽", use_container_width=True)

#     # 儲存到本地
#     save_path = os.path.join("data", "Aerophoto.jpg")
#     with open(save_path, "wb") as f:
#         f.write(uploaded_file.getbuffer())

#     st.success(f"✅ 圖片已儲存到：{save_path}")

import streamlit as st
# import os
from PIL import Image

st.header("🖼️ 土石流圖片")

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


# import streamlit as st
# import os
# from PIL import Image

# st.title("🖼️ 原始圖片可替換示範")

# # ---------- 初始化 ----------
# default_image_path = "data/Aerophoto.jpg"  # 預設圖片路徑

# # 初始化 session_state 變數
# if "show_uploader" not in st.session_state:
#     st.session_state.show_uploader = False

# if "current_image_path" not in st.session_state:
#     # 若沒有上傳過圖片，就顯示預設圖
#     st.session_state.current_image_path = default_image_path

# # ---------- 顯示目前的圖片 ----------
# if os.path.exists(st.session_state.current_image_path):
#     image = Image.open(st.session_state.current_image_path)
#     st.image(image, caption="目前顯示圖片", use_container_width=True)
# else:
#     st.warning("⚠️ 找不到預設圖片，請先上傳一張。")

# # ---------- 開關按鈕 ----------
# if st.button("📤 開啟 / 關閉 上傳介面"):
#     st.session_state.show_uploader = not st.session_state.show_uploader

# # ---------- 上傳介面 ----------
# if st.session_state.show_uploader:
#     st.info("請上傳新圖片以替換原圖")
#     uploaded_file = st.file_uploader("上傳圖片", type=["jpg", "jpeg", "png"])

#     if uploaded_file is not None:
#         # 儲存新圖片
#         new_path = os.path.join("data", "Aerophoto.jpg")
#         with open(new_path, "wb") as f:
#             f.write(uploaded_file.getbuffer())

#         # 更新目前圖片路徑
#         st.session_state.current_image_path = new_path

#         st.success("✅ 已成功替換圖片！")
#         st.image(Image.open(new_path), caption="新的圖片", use_container_width=True)
