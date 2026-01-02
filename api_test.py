import google.generativeai as genai


## GOOGLE_API_KEY = "AIzaSyAFffDRi6kpwxB29v082FuECkrjKAfpFP4" 

# 換成你新申請的 Key
genai.configure(api_key="AIzaSyCNVdra4vUidDFBxfiszkhOpd3FBg6WjVs")

try:
    print("--- 你目前金鑰可用的模型清單 ---")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"模型名稱: {m.name}")
except Exception as e:
    print(f"連線失敗，錯誤訊息: {e}")