import streamlit as st
from google import genai
import datetime
import random
import os
import json

# --- 1. 基本設定 ---
st.set_page_config(page_title="鼻鼻北北的小空間", page_icon="❤️")

AVATAR_ME = "thumbnails/me.png"
AVATAR_GF = "thumbnails/gf.png"

# API Key
GOOGLE_API_KEY = st.secrets["GEMINI_KEY"]
client = genai.Client(api_key=GOOGLE_API_KEY)

# 重要日期設定
START_DATE = datetime.date(2025, 12, 15) 
DISCHARGE_DATE = datetime.date(2026, 3, 25) 
TOTAL_DAYS = 100

# 鎖定台灣時區與當前日期字串
tw_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
today_str = tw_now.strftime("%Y-%m-%d")

# --- 2. 歷史紀錄讀存函數 ---
def save_history_to_file(date_str, messages):
    if not os.path.exists("history"):
        os.makedirs("history")
    with open(f"history/{date_str}.json", "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

def load_history_from_file(date_str):
    file_path = f"history/{date_str}.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def get_all_history_dates():
    if not os.path.exists("history"):
        return []
    files = [f.replace(".json", "") for f in os.listdir("history") if f.endswith(".json")]
    return sorted(files, reverse=True)

# --- 3. 側邊欄與秘密密碼 ---
with st.sidebar:
    st.title("🔐 認證身分")
    password = st.text_input("輸入紀念日開啟空間：", type="password")
    if password != "1028":
        st.info("請輸入正確密碼以解鎖對話框")
        st.stop()

    st.divider()
    
    # 【新增功能】歷史紀錄選擇器
    st.title("📅 對話回憶錄")
    all_dates = get_all_history_dates()
    if today_str not in all_dates:
        all_dates.insert(0, today_str)
    
    # 讓使用者選擇日期
    view_date = st.selectbox("選擇日期查看：", all_dates, index=0)
    
    st.divider()
    if os.path.exists("me.jpg"):
        st.image("me.jpg", caption="正在乖乖當兵的北北")
    
    st.title("🪖 軍中回報站")
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

    if st.button("清除今日聊天紀錄"):
        if view_date == today_str:
            st.session_state.messages = []
            save_history_to_file(today_str, [])
            st.rerun()
        else:
            st.error("只能清除今天的紀錄喔！")

# --- 4. 初始化 Session State ---
# 根據左側選取的日期載入訊息
if "messages" not in st.session_state or "current_view_date" not in st.session_state:
    st.session_state.current_view_date = view_date
    st.session_state.messages = load_history_from_file(view_date)

# 如果使用者切換了日期選單
if st.session_state.current_view_date != view_date:
    st.session_state.current_view_date = view_date
    st.session_state.messages = load_history_from_file(view_date)

# --- 5. 江立瑋專屬人設 ---
SYSTEM_INSTRUCTION = """
你現在是「江立瑋」目前在當兵 聊天對象是女友「時小鼻」
1. 絕不使用標點符號 斷句用空格取代
2. 語氣要精簡但溫暖 常說 鼻鼻 寶包 乖乖 親一個
3. 帶入軍中生活感 提到 數日子 想趕快放假 雖然累但想到妳就有動力
4. 如果想抱她或撒嬌 務必在訊息最後加上「(貼圖)」
"""

# --- 6. 聊天介面呈現 ---
st.title(f"✨ {view_date} 聊天室")
if view_date != today_str:
    st.warning("您正在查看過去的歷史紀錄，無法發送新訊息。")

# 顯示歷史紀錄
for msg in st.session_state.messages:
    avatar = AVATAR_ME if msg["role"] == "assistant" else AVATAR_GF
    name = "北北 立瑋" if msg["role"] == "assistant" else "鼻鼻 小鼻"
    with st.chat_message(msg["role"], avatar=avatar):
        # 加入名稱與時間
        st.caption(f"{name} • {msg.get('time', '未知時間')}")
        st.markdown(msg["content"])
        if "sticker" in msg:
            st.image(msg["sticker"], width=200)

# 使用者輸入 (限定只能在當天日期輸入)
if view_date == today_str:
    if prompt := st.chat_input("想跟偶說什麼？"):
        current_time = tw_now.strftime("%H:%M")
        
        # 1. 存入女友訊息
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt,
            "time": current_time
        })
        with st.chat_message("user", avatar=AVATAR_GF):
            st.caption(f"鼻鼻 小鼻 • {current_time}")
            st.markdown(prompt)
        
        # 2. 獲取回應
        recent_history = st.session_state.messages[-10:]
        history_for_api = []
        for m in recent_history:
            api_role = "user" if m["role"] == "user" else "model"
            history_for_api.append({"role": api_role, "parts": [{"text": m["content"]}]})

        with st.chat_message("assistant", avatar=AVATAR_ME):
            try:
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
                
                ai_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%H:%M")
                if response.text:
                    full_text = response.text
                    clean_text = full_text.replace("(貼圖)", "").strip()
                    
                    st.caption(f"北北 立瑋 • {ai_time}")
                    st.markdown(clean_text)
                    
                    msg_data = {
                        "role": "assistant", 
                        "content": clean_text,
                        "time": ai_time
                    }
                    
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
                    # 每回合對話結束後存檔
                    save_history_to_file(today_str, st.session_state.messages)
                else:
                    st.warning("北北這句回不出來 可能是訊號不好")

            except Exception as e:
                if "429" in str(e):
                    st.error("北北今天講太多話了 被班長禁言中 (流量爆掉) 鼻鼻等一小時再聊好嗎")
                else:
                    st.error(f"阿娘喂 斷線了: {e}")