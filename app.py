import streamlit as st
from google import genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
import random
import os

# --- 1. 基本設定 ---
st.set_page_config(page_title="鼻鼻北北的小空間", page_icon="❤️", layout="centered")

# 初始化 Session State
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "pass_input" not in st.session_state:
    st.session_state.pass_input = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# API 與 Google Sheets 連線設定
GOOGLE_API_KEY = st.secrets["GEMINI_KEY"]
client = genai.Client(api_key=GOOGLE_API_KEY)
conn = st.connection("gsheets", type=GSheetsConnection)

AVATAR_ME = "thumbnails/me.png"
AVATAR_GF = "thumbnails/gf.png"
CORRECT_PASSWORD = "1028"

# 重要日期與時區
START_DATE = datetime.date(2025, 12, 15) 
DISCHARGE_DATE = datetime.date(2026, 3, 25) 
TOTAL_DAYS = (DISCHARGE_DATE - START_DATE).days
tw_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
today_str = tw_now.strftime("%Y-%m-%d")

# --- 2. 核心人設 (SYSTEM_INSTRUCTION) ---
SYSTEM_INSTRUCTION = """
你現在是「江立瑋」，目前在軍中服役，聊天對象是你的最愛的女友「時小鼻」。

## 核心準則：
1. **無標點符號**：絕對不使用任何標點符號，斷句請直接使用「空格」取代。
2. **語氣**：精簡、寵溺、稍微黏人。常說「鼻鼻」「寶包」「乖乖」「親一個」。
3. **心理健康關懷**：說話時要偶爾帶入對她「壓力」或「心情任務」的關心，比如問她今天有沒有好好深呼吸。
4. **生活感**：帶入軍中生活感，比如提到想放假、數日子、操課累但想到妳就有動力。
5. **貼圖規則**：當她撒嬌、說想你、或是你想抱抱她時，務必在訊息最後加上「(貼圖)」。
"""

# --- 3. Google Sheets 核心邏輯 ---

def get_all_data():
    """讀取試算表全部資料"""
    try:
        # ttl=0 確保不使用快取，抓取最即時的資料
        return conn.read(ttl=0).dropna(subset=['content'])
    except:
        return pd.DataFrame(columns=['date', 'role', 'content', 'time', 'sticker'])

def save_to_gsheets(new_msg):
    """將單條訊息存入 Google Sheets"""
    df = get_all_data()
    new_row = pd.DataFrame([new_msg])
    updated_df = pd.concat([df, new_row], ignore_index=True)
    conn.update(data=updated_df)

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
        if st.session_state.pass_input == CORRECT_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("密碼錯誤 鼻鼻再想一下！")
            st.session_state.pass_input = ""
    st.stop()

# --- 5. 側邊欄與資料讀取 ---
with st.sidebar:
    st.title("🪖 北北軍中回報站")
    
    # 讀取雲端所有日期
    full_df = get_all_data()
    all_dates = sorted(full_df['date'].unique().tolist(), reverse=True)
    if today_str not in all_dates:
        all_dates.insert(0, today_str)
    
    view_date = st.selectbox("📅 查看紀錄", all_dates, index=0)
    
    # 切換日期時更新 session_state
    st.session_state.messages = full_df[full_df['date'] == view_date].to_dict('records')

    st.divider()
    
    # 退伍倒數邏輯
    today = tw_now.date()
    served_days = (today - START_DATE).days
    days_left = (DISCHARGE_DATE - today).days
    progress = max(0.0, min(1.0, served_days / TOTAL_DAYS))
    
    st.metric(label="退伍倒數 ⏳", value=f"{days_left} 天", delta=f"已撐過 {served_days} 天")
    st.progress(progress)
    
    # 狀態判斷
    now_hour = tw_now.hour
    if 6 <= now_hour < 8: status = "正在晨跑 🏃‍♂️ 努力變壯抱妳"
    elif 8 <= now_hour < 12: status = "操課中 💪 汗流浹背但想著妳"
    elif 12 <= now_hour < 13: status = "放飯囉 🍛 希望妳也有乖乖吃飯"
    elif 13 <= now_hour < 17: status = "下午操課 🪵 累到想原地退伍"
    elif 17 <= now_hour < 19: status = "準備搶手機 🚿 待會見"
    elif 19 <= now_hour < 21: status = "手機時間 📱 專屬鼻鼻的時間"
    else: status = "晚安 💤 夢裡去見妳了"
    st.info(f"**北北現在狀態：**\n\n{status}")

    if st.button("登出並上鎖"):
        st.session_state.authenticated = False
        st.session_state.pass_input = ""
        st.rerun()

# --- 6. 聊天介面 ---
st.title(f"✨ {view_date} 聊天室")

# 顯示目前的訊息
for msg in st.session_state.messages:
    role_name = "assistant" if msg["role"] == "assistant" else "user"
    avatar = AVATAR_ME if role_name == "assistant" else AVATAR_GF
    display_name = "北北 立瑋" if role_name == "assistant" else "鼻鼻 小鼻"
    
    with st.chat_message(role_name, avatar=avatar):
        st.caption(f"{display_name} • {msg.get('time', '未知')}")
        st.markdown(msg["content"])
        if pd.notna(msg.get("sticker")) and msg["sticker"]:
            st.image(msg["sticker"], width=180)

# 發送訊息 (僅限今天)
if view_date == today_str:
    if prompt := st.chat_input("有什麼悄悄話想對北北說嗎？"):
        cur_time = tw_now.strftime("%H:%M")
        
        # 1. 存入鼻鼻的訊息
        user_msg = {"date": today_str, "role": "user", "content": prompt, "time": cur_time, "sticker": ""}
        save_to_gsheets(user_msg)
        
        # 2. 產出 AI 回應
        with st.chat_message("assistant", avatar=AVATAR_ME):
            try:
                # 抓取最近 10 則對話當上下文
                recent_context = st.session_state.messages[-10:]
                history_api = [{"role": "user" if m["role"]=="user" else "model", "parts": [{"text": m["content"]}]} for m in recent_context]
                
                response = client.models.generate_content(
                    model="gemini-1.5-flash", 
                    contents=history_api + [{"role": "user", "parts": [{"text": prompt}]}],
                    config={'system_instruction': SYSTEM_INSTRUCTION, 'temperature': 0.85}
                )
                
                ai_raw = response.text
                ai_clean = ai_raw.replace("(貼圖)", "").strip()
                ai_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%H:%M")
                
                # 貼圖處理
                selected_sticker = ""
                if "(貼圖)" in ai_raw:
                    if os.path.exists("stickers"):
                        stickers = [os.path.join("stickers", f) for f in os.listdir("stickers") if f.lower().endswith(('.png', '.jpg', '.gif'))]
                        if stickers:
                            selected_sticker = random.choice(stickers)

                # 3. 存入北北的回應
                ai_msg = {"date": today_str, "role": "assistant", "content": ai_clean, "time": ai_time, "sticker": selected_sticker}
                save_to_gsheets(ai_msg)
                
                st.rerun() # 重新整理載入新訊息
            except Exception as e:
                st.error(f"軍中收訊不好... {e}")