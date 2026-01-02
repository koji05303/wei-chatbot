import streamlit as st
from google import genai
import datetime
import random
import os
import json

# --- 1. 基本設定 ---
st.set_page_config(page_title="鼻鼻北北的秘密基地", page_icon="❤️")

AVATAR_ME = "thumbnails/me.png"
AVATAR_GF = "thumbnails/gf.png"

# API Key
GOOGLE_API_KEY = st.secrets["GEMINI_KEY"] 
client = genai.Client(api_key=GOOGLE_API_KEY)

# 重要日期
START_DATE = datetime.date(2025, 12, 15) 
DISCHARGE_DATE = datetime.date(2026, 3, 25) 
TOTAL_DAYS = 100

# 時區處理
tw_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
today_str = tw_now.strftime("%Y-%m-%d")

# --- 2. 歷史紀錄讀存邏輯 ---
def save_history(messages):
    if not os.path.exists("history"):
        os.makedirs("history")
    with open(f"history/{today_str}.json", "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

def load_history(date_str):
    file_path = f"history/{date_str}.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# --- 3. 側邊欄：歷史紀錄與回報 ---
with st.sidebar:
    st.title("🔐 認證身分")
    password = st.text_input("輸入紀念日：", type="password")
    if password != "1028":
        st.info("請輸入正確密碼")
        st.stop()

    st.divider()
    st.title("追蹤對話紀錄")
    
    # 讀取 history 資料夾中的所有日期
    if os.path.exists("history"):
        history_files = sorted([f.replace(".json", "") for f in os.listdir("history") if f.endswith(".json")], reverse=True)
    else:
        history_files = []

    # 選擇查看哪天的紀錄
    selected_date = st.selectbox("切換歷史紀錄：", ["今天"] + history_files)
    
    st.divider()
    st.title("🪖 軍中回報站")
    # ... (原本的進度條與狀態顯示邏輯保持不變)
    st.info(f"**今天日期：** {today_str}")

# --- 4. 初始化 Session State ---
if "messages" not in st.session_state:
    # 如果選擇的是過去的日期，就載入那天的紀錄
    if selected_date != "今天":
        st.session_state.messages = load_history(selected_date)
    else:
        # 否則載入今天的存檔
        st.session_state.messages = load_history(today_str)

# 如果使用者在側邊欄切換了日期，強制更新 session_state
if selected_date != "今天":
    st.session_state.messages = load_history(selected_date)
    st.warning(f"正在查看 {selected_date} 的紀錄 (唯讀)")

# --- 5. 聊天介面 ---
st.title("✨ 鼻鼻專屬聊天室")

# 顯示訊息
for msg in st.session_state.messages:
    avatar = AVATAR_ME if msg["role"] == "assistant" else AVATAR_GF
    # 根據角色設定名稱
    display_name = "北北 立瑋" if msg["role"] == "assistant" else "鼻鼻 小鼻"
    
    with st.chat_message(msg["role"], avatar=avatar):
        # 顯示名稱與時間
        st.caption(f"{display_name} • {msg.get('time', '')}")
        st.markdown(msg["content"])
        if "sticker" in msg:
            st.image(msg["sticker"], width=200)

# 使用者輸入 (只有在「今天」模式下才能輸入)
if selected_date == "今天":
    if prompt := st.chat_input("想跟北北說什麼？"):
        current_time = tw_now.strftime("%H:%M")
        
        # 1. 存入女友訊息
        user_msg = {"role": "user", "content": prompt, "time": current_time}
        st.session_state.messages.append(user_msg)
        
        # 顯示
        with st.chat_message("user", avatar=AVATAR_GF):
            st.caption(f"鼻鼻 小鼻 • {current_time}")
            st.markdown(prompt)
        
        # 2. 獲取回應
        with st.chat_message("assistant", avatar=AVATAR_ME):
            try:
                # 只取最近 10 句做記憶
                recent_history = st.session_state.messages[-10:]
                history_for_api = [{"role": "user" if m["role"]=="user" else "model", "parts": [{"text": m["content"]}]} for m in recent_history]

                response = client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=history_for_api,
                    config={'system_instruction': "你現在是江立瑋... (略)"} # 這裡放之前的人設
                )
                
                ai_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%H:%M")
                clean_text = response.text.replace("(貼圖)", "").strip()
                st.caption(f"北北 立瑋 • {ai_time}")
                st.markdown(clean_text)
                
                ai_msg = {"role": "assistant", "content": clean_text, "time": ai_time}
                
                # 貼圖處理
                if "(貼圖)" in response.text:
                    sticker_folder = "stickers"
                    stickers = [os.path.join(sticker_folder, f) for f in os.listdir(sticker_folder) if f.lower().endswith(('.png', '.jpg'))]
                    if stickers:
                        sel_sticker = random.choice(stickers)
                        st.image(sel_sticker, width=200)
                        ai_msg["sticker"] = sel_sticker

                st.session_state.messages.append(ai_msg)
                
                # 存檔至 JSON
                save_history(st.session_state.messages)

            except Exception as e:
                st.error(f"連線中斷：{e}")