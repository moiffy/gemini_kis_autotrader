import google.generativeai as genai

# Gemini API 키 설정
API_KEY = "****"
genai.configure(api_key=API_KEY)

print("--- [가용한 제미나이 모델 목록] ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Model Name: {m.name}")
except Exception as e:
    print(f"Error listing models: {str(e)}")
