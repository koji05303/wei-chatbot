import streamlit as st
from google import genai
import datetime
import random
import os
import json

# --- 1. 基本設定 ---
st.set_page_config(page_title="鼻鼻北北的小空間", page_icon="❤️", layout="centered")

AVATAR_ME = "thumbnails/me.png"
AVATAR_GF = "thumbnails/gf.png"
CORRECT_PASSWORD = "1028" # 你的密碼

# 初始化 Session State
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "pass_input" not in st.session_state:
    st.session_state.pass_input = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# API Key (請確保在 Streamlit Cloud Secrets 設定 GEMINI_KEY)
GOOGLE_API_KEY = st.secrets["GEMINI_KEY"]
client = genai.Client(api_key=GOOGLE_API_KEY)

# 重要日期設定
START_DATE = datetime.date(2025, 12, 15) 
DISCHARGE_DATE = datetime.date(2026, 3, 25) 
TOTAL_DAYS = 100

# 鎖定台灣時區
tw_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
today_str = tw_now.strftime("%Y-%m-%d")

# --- 2. 核心人物設定 (SYSTEM_INSTRUCTION) ---
# 這裡就是你的靈魂所在！
SYSTEM_INSTRUCTION = """
你現在是「江立瑋」目前在當兵 聊天對象是女友「時小鼻」

## 核心準則：
1. **無標點符號**：絕對不使用任何標點符號 斷句請直接使用「空格」取代
2. **語氣**：精簡 寵溺 稍微有點黏人 但不油膩 常說「鼻鼻」「寶包」「乖乖」「親一個」
3. **增加溫度**：回話要帶入軍中生活感 比如提到 數日子 想趕快放假 裡面很累但想到妳就有動力
4. **貼圖規則**：當她撒嬌、說想你、或是你想抱抱她時 務必在訊息最後加上「(貼圖)」

## 語氣範例：
- 她說想你：我也好想妳 真的 每天在裡面最期待就是這時候可以跟妳講話 (貼圖)
- 她說真的嗎：真的啦 騙妳幹嘛 我在裡面每天都在看照片數日子 (貼圖) 愛妳啦
- 她抱怨生活：寶包辛苦了 我不在妳身邊要乖乖喔 回去一定好好抱妳 真的好想妳 (貼圖)
"""

# --- 3. 輔助函數 ---
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

# --- 4. 解鎖畫面 (螢幕小鍵盤) ---
if not st.session_state.authenticated:
    st.write("<h1 style='text-align: center;'>🔐 認證身分</h1>", unsafe_allow_html=True)
    st.write("<p style='text-align: center;'>請輸入紀念日解鎖北北的小空間</p>", unsafe_allow_html=True)
    
    pass_display = " ".join(["●" if i < len(st.session_state.pass_input) else "○" for i in range(4)])
    st.write(f"<h2 style='text-align: center; letter-spacing: 10px;'>{pass_display}</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    keys = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["清空", "0", "←"]]

    for j, row in enumerate(keys):
        for k, key in enumerate(row):
            with [col1, col2, col3][k]:
                if st.button(key, use_container_width=True, key=f"key_{key}"):
                    if key == "清空": st.session_state.pass_input = ""
                    elif key == "←": st.session_state.pass_input = st.session_state.pass_input[:-1]
                    elif len(st.session_state.pass_input) < 4: st.session_state.pass_input += key
                    st.rerun()

    st.write("---")
    if st.button("🔓 確認解鎖", use_container_width=True):
        if st.session_state.pass_input == CORRECT_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("密碼錯誤，鼻鼻再想一下！")
            st.session_state.pass_input = ""
    st.stop()

# --- 5. 側邊欄 (解鎖後顯示) ---
with st.sidebar:
    st.title("🪖 軍中回報站")
    all_dates = get_all_history_dates()
    if today_str not in all_dates: all_dates.insert(0, today_str)
    view_date = st.selectbox("📅 歷史紀錄", all_dates, index=0)
    
    if "current_view_date" not in st.session_state or st.session_state.current_view_date != view_date:
        st.session_state.current_view_date = view_date
        st.session_state.messages = load_history_from_file(view_date)

    st.divider()
    if os.path.exists("me.jpg"):
        st.image("me.jpg", caption="正在乖乖當兵的北北")
    
    today = tw_now.date()
    now_hour = tw_now.hour
    served_days = (today - START_DATE).days
    days_left = (DISCHARGE_DATE - today).days
    progress = max(0, min(100, served_days)) / TOTAL_DAYS
    st.metric(label="退伍倒數", value=f"{days_left} 天")
    st.progress(progress)
    
    if 6 <= now_hour < 8: status = "早安 晨操跑步中 🏃‍♂️"
    elif 8 <= now_hour < 12: status = "操課中... 💪"
    elif 12 <= now_hour < 13: status = "放飯時間 😂"
    elif 13 <= now_hour < 17: status = "下午操課 想妳 ❤️"
    elif 17 <= now_hour < 19: status = "準備搶手機中！"
    elif 19 <= now_hour < 21: status = "手機時間 陪妳聊天 📱"
    else: status = "晚安 夢到妳了 😴"
    st.info(f"**北北狀態：**\n\n{status}")

    if st.button("登出並上鎖"):
        st.session_state.authenticated = False
        st.session_state.pass_input = ""
        st.rerun()

# --- 6. 聊天介面 ---
st.title(f"✨ {view_date} 聊天室")

for msg in st.session_state.messages:
    avatar = AVATAR_ME if msg["role"] == "assistant" else AVATAR_GF
    name = "北北 立瑋" if msg["role"] == "assistant" else "鼻鼻 小鼻"
    with st.chat_message(msg["role"], avatar=avatar):
        st.caption(f"{name} • {msg.get('time', '未知時間')}")
        st.markdown(msg["content"])
        if "sticker" in msg: st.image(msg["sticker"], width=200)

if view_date == today_str:
    if prompt := st.chat_input("想跟北北說什麼？"):
        cur_time = tw_now.strftime("%H:%M")
        st.session_state.messages.append({"role": "user", "content": prompt, "time": cur_time})
        with st.chat_message("user", avatar=AVATAR_GF):
            st.caption(f"鼻鼻 小鼻 • {cur_time}")
            st.markdown(prompt)
        
        with st.chat_message("assistant", avatar=AVATAR_ME):
            try:
                # 這裡使用了最上面定義的完整人設
                recent = st.session_state.messages[-10:]
                history_api = [{"role": "user" if m["role"]=="user" else "model", "parts": [{"text": m["content"]}]} for m in recent]
                
                response = client.models.generate_content(
                    model="gemini-flash-latest", 
                    contents=history_api,
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
                clean_text = response.text.replace("(貼圖)", "").strip()
                st.caption(f"北北 立瑋 • {ai_time}")
                st.markdown(clean_text)
                
                msg_data = {"role": "assistant", "content": clean_text, "time": ai_time}
                if "(貼圖)" in response.text:
                    sticker_folder = "stickers"
                    if os.path.exists(sticker_folder):
                        stickers = [os.path.join(sticker_folder, f) for f in os.listdir(sticker_folder) if f.lower().endswith(('.png', '.jpg'))]
                        if stickers:
                            selected_sticker = random.choice(stickers)
                            st.image(selected_sticker, width=200)
                            msg_data["sticker"] = selected_sticker
                
                st.session_state.messages.append(msg_data)
                save_history_to_file(today_str, st.session_state.messages)
            except Exception as e:
                st.error(f"北北斷線了：{e}")