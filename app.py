import streamlit as st
from google import genai
import datetime
import random
import os

# --- 1. 基本設定 ---
st.set_page_config(page_title="鼻鼻北北的小空間", page_icon="❤️")

AVATAR_ME = "thumbnails/me.png"
AVATAR_GF = "thumbnails/gf.png"

# API Key (請確保這裡填入你的金鑰)
GOOGLE_API_KEY = st.secrets["GEMINI_KEY"]
client = genai.Client(api_key=GOOGLE_API_KEY)

# 重要日期設定
START_DATE = datetime.date(2025, 12, 15) 
DISCHARGE_DATE = datetime.date(2026, 3, 25) 
TOTAL_DAYS = 100

# --- 2. 初始化 Session State (這是解決錯誤的關鍵) ---
# 必須放在所有邏輯的最前面
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. 側邊欄與秘密密碼 ---
with st.sidebar:
    st.title("🔐 認證身分")
    # 建議把 '0520' 改成你們的紀念日
    password = st.text_input("輸入紀念日開啟空間：", type="password")
    if password != "1028":
        st.info("請輸入正確密碼以解鎖對話框")
        st.stop() # 沒輸入正確密碼，後面的程式都不會執行

    st.divider()
    if os.path.exists("me.jpg"):
        st.image("me.jpg", caption="正在乖乖當兵的北北")
    
    st.title("🪖 軍中回報站")
    # 鎖定台灣時區
    tw_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    today = tw_now.date()
    now_hour = tw_now.hour

    served_days = (today - START_DATE).days
    days_left = (DISCHARGE_DATE - today).days
    progress = max(0, min(100, served_days)) / TOTAL_DAYS
    
    st.metric(label="距離退伍還有", value=f"{days_left} 天")
    st.progress(progress)
    
    st.divider()
    if 6 <= now_hour < 8: status = "早安 正在晨操跑步中 🏃‍♂️"
    elif 8 <= now_hour < 12: status = "操課中... 💪"
    elif 12 <= now_hour < 13: status = "放飯時間 😂"
    elif 13 <= now_hour < 17: status = "下午繼續操課 想妳中 ❤️"
    elif 17 <= now_hour < 19: status = "吃晚餐 準備搶手機！"
    elif 19 <= now_hour < 21: status = "手機時間 正在陪妳聊天 📱"
    else: status = "晚安 已經躺平夢到妳了 😴"
    st.info(f"**北北狀態：**\n\n{status}")

    if st.button("清除聊天紀錄"):
        st.session_state.messages = []
        st.rerun()

# --- 4. 江立瑋專屬人設 ---
SYSTEM_INSTRUCTION = """
你現在是「江立瑋」目前在當兵 聊天對象是女友「時小鼻」
1. 絕不使用標點符號 斷句用空格取代
2. 語氣要精簡但溫暖 常說 鼻鼻 寶包 乖乖 親一個
3. 帶入軍中生活感 提到 數日子 想趕快放假 雖然累但想到妳就有動力
4. 如果想抱她或撒嬌 務必在訊息最後加上「(貼圖)」
"""

# --- 5. 聊天介面呈現 ---
st.title("✨ 鼻鼻專屬聊天室")

# 顯示歷史紀錄
for msg in st.session_state.messages:
    avatar = AVATAR_ME if msg["role"] == "assistant" else AVATAR_GF
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if "sticker" in msg:
            st.image(msg["sticker"], width=200)

# 使用者輸入
if prompt := st.chat_input("想跟偶說什麼？"):
    # 存入女友訊息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=AVATAR_GF):
        st.markdown(prompt)
    
    # 【流量優化】只取最近 10 句，防止 Token 爆掉 (429 錯誤)
    recent_history = st.session_state.messages[-10:]
    
    history_for_api = []
    for m in recent_history:
        api_role = "user" if m["role"] == "user" else "model"
        history_for_api.append({"role": api_role, "parts": [{"text": m["content"]}]})

    # 獲取回應
    with st.chat_message("assistant", avatar=AVATAR_ME):
        try:
            # 改用配額較多的 1.5-flash
            response = client.models.generate_content(
                model="gemini-flash-latest", 
                contents=history_for_api,
                config={
                    'system_instruction': SYSTEM_INSTRUCTION,
                    'max_output_tokens': 300,
                    'temperature': 0.9,
                    'safety_settings': [
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                    ]
                }
            )
            
            if response.text:
                full_text = response.text
                clean_text = full_text.replace("(貼圖)", "").strip()
                st.markdown(clean_text)
                
                msg_data = {"role": "assistant", "content": clean_text}
                
                # 貼圖邏輯
                if "(貼圖)" in full_text:
                    sticker_folder = "stickers"
                    if os.path.exists(sticker_folder):
                        stickers = [os.path.join(sticker_folder, f) for f in os.listdir(sticker_folder) 
                                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                        if stickers:
                            selected_sticker = random.choice(stickers)
                            st.image(selected_sticker, width=200)
                            msg_data["sticker"] = selected_sticker
                
                st.session_state.messages.append(msg_data)
            else:
                st.warning("北北這句回不出來 可能是訊號不好")

        except Exception as e:
            if "429" in str(e):
                st.error("北北今天講太多話了 被班長禁言中 (流量爆掉) 鼻鼻等一小時再聊好嗎")
            else:
                st.error(f"阿娘喂 斷線了: {e}")