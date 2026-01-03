import streamlit as st
from google import genai
import datetime
import random
import os
import json
import zipfile
import io

# --- 1. 基本設定與聊天軟體風格 CSS ---
st.set_page_config(page_title="鼻鼻北北的小空間", page_icon="❤️", layout="centered")

# 注入 CSS：保留圓角與陰影，但不強制背景色，讓它跟隨預設模式
st.markdown("""
    <style>
    /* 側邊欄樣式 - 移除強制背景色 */
    section[data-testid="stSidebar"] {
        border-right: 1px solid #ddd;
    }

    /* 聊天氣泡圓角化與陰影 */
    [data-testid="stChatMessage"] {
        border-radius: 20px;
        padding: 10px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* 隱藏頂部裝飾 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 輸入框邊距優化 */
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 初始化 Session State
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "pass_input" not in st.session_state:
    st.session_state.pass_input = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# API Key
try:
    GOOGLE_API_KEY = st.secrets["GEMINI_KEY"]
    client = genai.Client(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error("找不到 API Key，請檢查 Streamlit Secrets 設定！")

# 重要日期
START_DATE = datetime.date(2025, 12, 15) 
DISCHARGE_DATE = datetime.date(2026, 3, 25) 
TOTAL_DAYS = (DISCHARGE_DATE - START_DATE).days
tw_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
today_str = tw_now.strftime("%Y-%m-%d")

# --- 2. 核心人設 ---
SYSTEM_INSTRUCTION = """
你現在是「江立瑋」目前在當兵 聊天對象是女友「時小鼻」
## 核心準則：
1. **無標點符號**：絕對不使用任何標點符號 斷句直接使用空格取代
2. **語氣**：精簡 寵溺 稍微黏人 常說「鼻鼻」「寶包」「乖乖」「親一個」
3. **生活感**：回話要帶入軍中感 提到數日子 想趕快放假 裡面很累但想到妳就有動力
4. **貼圖規則**：當她撒嬌、說想你、或是你想抱抱她時 務必在訊息最後加上「(貼圖)」
"""

# --- 3. 檔案輔助函數 ---
HISTORY_FOLDER = "history"

def save_history_to_file(date_str, messages):
    if not os.path.exists(HISTORY_FOLDER): os.makedirs(HISTORY_FOLDER)
    with open(f"{HISTORY_FOLDER}/{date_str}.json", "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

def load_history_from_file(date_str):
    file_path = f"{HISTORY_FOLDER}/{date_str}.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f: return json.load(f)
    return []

def get_all_history_dates():
    if not os.path.exists(HISTORY_FOLDER): return []
    files = [f.replace(".json", "") for f in os.listdir(HISTORY_FOLDER) if f.endswith(".json")]
    return sorted(files, reverse=True)

def create_zip_of_history():
    if not os.path.exists(HISTORY_FOLDER) or not os.listdir(HISTORY_FOLDER): return None
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(HISTORY_FOLDER):
            for file in files: zf.write(os.path.join(root, file), file)
    return buf.getvalue()

# --- 4. 解鎖畫面 ---
if not st.session_state.authenticated:
    st.write("<h1 style='text-align: center; color: #ff4b4b;'>❤️ 鼻鼻北北的小空間</h1>", unsafe_allow_html=True)
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
    if st.button("🔓 進入聊天室", use_container_width=True):
        if st.session_state.pass_input == "1028":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("密碼錯誤 鼻鼻再想一下！")
            st.session_state.pass_input = ""
    st.stop()

# --- 5. 側邊欄設計 ---
with st.sidebar:
    if os.path.exists("me.jpg"):
        st.image("me.jpg", use_container_width=True, caption="📸 北北(狗狗版)")

    st.title("🪖 軍中回報站")
    
    all_dates = get_all_history_dates()
    if today_str not in all_dates: all_dates.insert(0, today_str)
    view_date = st.selectbox("📅 選擇聊天日期", all_dates, index=0)
    
    if "current_view_date" not in st.session_state or st.session_state.current_view_date != view_date:
        st.session_state.current_view_date = view_date
        st.session_state.messages = load_history_from_file(view_date)

    st.divider()
    
    today = tw_now.date()
    served_days = (today - START_DATE).days
    days_left = (DISCHARGE_DATE - today).days
    progress = max(0.0, min(1.0, served_days / TOTAL_DAYS))
    st.metric(label="退伍倒數 ⏳", value=f"{days_left} 天", delta=f"已服務 {served_days} 天")
    st.progress(progress)
    
    now_hour = tw_now.hour
    if 6 <= now_hour < 8: status = "正在晨跑 🏃‍♂️ 努力跑3000趕快出來抱妳"
    elif 8 <= now_hour < 12: status = "操課中 💪 流口水想著妳"
    elif 12 <= now_hour < 13: status = "放飯吃廚餘囉 🍛 鼻鼻要多吃一點"
    elif 13 <= now_hour < 17: status = "下午操課 看班長耍智障 🪵 累到想原地退伍"
    elif 17 <= now_hour < 19: status = "洗澡搶浴室 🚿 準備待會見"
    elif 19 <= now_hour < 21: status = "準備搶手機時間 📱 專屬鼻鼻的時間"
    else: status = "晚安 💤 強迫就寢 偶要在夢裡見泥了"
    st.success(f"**北北動態：**\n\n{status}")

    st.divider()
    zip_data = create_zip_of_history()
    if zip_data:
        st.download_button(label="📥 下載所有對話 (ZIP)", data=zip_data, file_name=f"love_history_{today_str}.zip", mime="application/zip", use_container_width=True)

    if st.button("🚪 登出並上鎖", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.pass_input = ""
        st.rerun()

# --- 6. 聊天介面 ---
st.write(f"### ✨ {view_date} 聊天室")

AVATAR_ME = "thumbnails/me.png"
AVATAR_GF = "thumbnails/gf.png"

for msg in st.session_state.messages:
    is_ai = msg["role"] == "assistant"
    avatar = AVATAR_ME if is_ai else AVATAR_GF
    name = "北北 立瑋" if is_ai else "鼻鼻 小鼻"
    
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(f"**{name}** <span style='color:gray; font-size:0.8em;'>{msg.get('time', '')}</span>", unsafe_allow_html=True)
        st.markdown(msg["content"])
        if "sticker" in msg and msg["sticker"]:
            st.image(msg["sticker"], width=160)

# 發送新訊息
if view_date == today_str:
    if prompt := st.chat_input("想對北北說什麼呢？"):
        cur_time = tw_now.strftime("%H:%M")
        
        # 1. 先加入使用者訊息
        st.session_state.messages.append({"role": "user", "content": prompt, "time": cur_time})
        st.rerun() # 立即渲染顯示使用者的對話氣泡

# 2. 處理助理回應 (如果最後一則是使用者發的)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant", avatar=AVATAR_ME):
        try:
            # 準備歷史紀錄，確保角色交替：user -> model -> user
            recent = st.session_state.messages[-12:]
            history_api = []
            for m in recent:
                role = "user" if m["role"] == "user" else "model"
                history_api.append({"role": role, "parts": [{"text": m["content"]}]})
            
            response = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=history_api,
                config={'system_instruction': SYSTEM_INSTRUCTION, 'temperature': 0.85}
            )
            
            ai_raw = response.text
            ai_clean = ai_raw.replace("(貼圖)", "").strip()
            ai_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%H:%M")
            
            sticker_path = None
            if "(貼圖)" in ai_raw:
                if os.path.exists("stickers"):
                    stickers = [os.path.join("stickers", f) for f in os.listdir("stickers") if f.lower().endswith(('.png', '.jpg', '.gif'))]
                    if stickers: sticker_path = random.choice(stickers)
            
            msg_data = {"role": "assistant", "content": ai_clean, "time": ai_time, "sticker": sticker_path}
            st.session_state.messages.append(msg_data)
            save_history_to_file(today_str, st.session_state.messages)
            st.rerun()
            
        except Exception as e:
            st.error(f"軍中收訊不好... 斷線了 (原因: {str(e)})")