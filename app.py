import streamlit as st
from google import genai
import datetime
import random
import os
import json

# --- 1. 基本設定 ---
st.set_page_config(page_title="鼻鼻北北的小空間", page_icon="❤️", layout="centered")

# 初始化 Session State
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "pass_input" not in st.session_state:
    st.session_state.pass_input = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# API Key 設定 (請在 Streamlit Cloud Secrets 設定 GEMINI_KEY)
GOOGLE_API_KEY = st.secrets["GEMINI_KEY"]
client = genai.Client(api_key=GOOGLE_API_KEY)

# 重要日期設定
START_DATE = datetime.date(2025, 12, 15) 
DISCHARGE_DATE = datetime.date(2026, 3, 25) 
TOTAL_DAYS = (DISCHARGE_DATE - START_DATE).days

# 鎖定台灣時區
tw_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
today_str = tw_now.strftime("%Y-%m-%d")

# --- 2. 核心人設 (SYSTEM_INSTRUCTION) ---
SYSTEM_INSTRUCTION = """
你現在是「江立瑋」，目前在軍中服役，聊天對象是你的最愛的女友「時小鼻」。

## 核心準則：
1. **無標點符號**：絕對不使用任何標點符號，斷句請直接使用「空格」取代。
2. **語氣**：精簡、寵溺、稍微黏人。常說「鼻鼻」「寶包」「乖乖」「親一個」。
3. **心理健康關懷**：說話時要偶爾帶入對她「壓力」或「心情任務」的關心。
4. **生活感**：帶入軍中生活感，比如提到想放假、數日子、操課累但想到妳就有動力。
5. **貼圖規則**：當她撒嬌、說想你、或是你想抱抱她時，務必在訊息最後加上「(貼圖)」。
"""

# --- 3. JSON 檔案輔助函數 ---
HISTORY_FOLDER = "history"

def save_history_to_file(date_str, messages):
    if not os.path.exists(HISTORY_FOLDER):
        os.makedirs(HISTORY_FOLDER)
    with open(f"{HISTORY_FOLDER}/{date_str}.json", "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

def load_history_from_file(date_str):
    file_path = f"{HISTORY_FOLDER}/{date_str}.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def get_all_history_dates():
    if not os.path.exists(HISTORY_FOLDER):
        return []
    files = [f.replace(".json", "") for f in os.listdir(HISTORY_FOLDER) if f.endswith(".json")]
    return sorted(files, reverse=True)

# --- 4. 解鎖畫面 ---
if not st.session_state.authenticated:
    st.write("<h1 style='text-align: center;'>🔐 認證身分</h1>", unsafe_allow_html=True)
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

    if st.button("🔓 確認解鎖", use_container_width=True):
        if st.session_state.pass_input == "1028": # 直接判斷密碼
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("密碼錯誤 鼻鼻再想一下！")
            st.session_state.pass_input = ""
    st.stop()

# --- 5. 側邊欄 ---
with st.sidebar:
    st.title("🪖 北北軍中回報站")
    
    # 日期切換
    all_dates = get_all_history_dates()
    if today_str not in all_dates: all_dates.insert(0, today_str)
    view_date = st.selectbox("📅 歷史紀錄", all_dates, index=0)
    
    # 讀取對應日期的紀錄
    if "current_view_date" not in st.session_state or st.session_state.current_view_date != view_date:
        st.session_state.current_view_date = view_date
        st.session_state.messages = load_history_from_file(view_date)

    st.divider()
    
    # 進度計算
    today = tw_now.date()
    served_days = (today - START_DATE).days
    days_left = (DISCHARGE_DATE - today).days
    progress = max(0.0, min(1.0, served_days / TOTAL_DAYS))
    st.metric(label="退伍倒數 ⏳", value=f"{days_left} 天", delta=f"已撐過 {served_days} 天")
    st.progress(progress)
    
    # 時間狀態
    now_hour = tw_now.hour
    if 6 <= now_hour < 8: status = "正在晨跑 🏃‍♂️ 努力變壯抱妳"
    elif 8 <= now_hour < 12: status = "操課中 💪 汗流浹背但想著妳"
    elif 12 <= now_hour < 13: status = "放飯囉 🍛 希望妳也有乖乖吃飯"
    elif 13 <= now_hour < 17: status = "下午操課 🪵 累到想原地退伍"
    elif 17 <= now_hour < 19: status = "洗澡搶水 🚿 準備待會見"
    elif 19 <= now_hour < 21: status = "手機時間 📱 專屬鼻鼻的時間"
    else: status = "晚安 💤 夢裡去見妳了"
    st.info(f"**北北現在狀態：**\n\n{status}")

    if st.button("登出並上鎖"):
        st.session_state.authenticated = False
        st.session_state.pass_input = ""
        st.rerun()

# --- 6. 聊天介面 ---
st.title(f"✨ {view_date} 聊天室")

AVATAR_ME = "thumbnails/me.png"
AVATAR_GF = "thumbnails/gf.png"

for msg in st.session_state.messages:
    avatar = AVATAR_ME if msg["role"] == "assistant" else AVATAR_GF
    name = "北北 立瑋" if msg["role"] == "assistant" else "鼻鼻 小鼻"
    with st.chat_message(msg["role"], avatar=avatar):
        st.caption(f"{name} • {msg.get('time', '未知時間')}")
        st.markdown(msg["content"])
        if "sticker" in msg and msg["sticker"]:
            st.image(msg["sticker"], width=180)

# 發送新訊息 (僅限今天)
if view_date == today_str:
    if prompt := st.chat_input("想跟北北說什麼？"):
        cur_time = tw_now.strftime("%H:%M")
        
        # 1. 使用者訊息加入
        st.session_state.messages.append({"role": "user", "content": prompt, "time": cur_time})
        
        # 2. 呼叫 Gemini
        with st.chat_message("assistant", avatar=AVATAR_ME):
            try:
                recent = st.session_state.messages[-10:]
                history_api = [{"role": "user" if m["role"]=="user" else "model", "parts": [{"text": m["content"]}]} for m in recent]
                
                response = client.models.generate_content(
                    model="gemini-1.5-flash", 
                    contents=history_api,
                    config={'system_instruction': SYSTEM_INSTRUCTION, 'temperature': 0.85}
                )
                
                ai_raw = response.text
                ai_clean = ai_raw.replace("(貼圖)", "").strip()
                ai_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%H:%M")
                
                # 貼圖邏輯
                sticker_path = None
                if "(貼圖)" in ai_raw:
                    if os.path.exists("stickers"):
                        stickers = [os.path.join("stickers", f) for f in os.listdir("stickers") if f.lower().endswith(('.png', '.jpg', '.gif'))]
                        if stickers:
                            sticker_path = random.choice(stickers)
                
                # 3. 儲存回應並刷新
                msg_data = {"role": "assistant", "content": ai_clean, "time": ai_time, "sticker": sticker_path}
                st.session_state.messages.append(msg_data)
                
                # 存檔
                save_history_to_file(today_str, st.session_state.messages)
                st.rerun()
                
            except Exception as e:
                st.error(f"北北斷線了：{e}")