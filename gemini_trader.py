import google.generativeai as genai
import json

# Gemini API 키 설정
API_KEY = "****"
genai.configure(api_key=API_KEY)

def get_trading_decision(stock_name, current_price, change_rate, balance):
    """지정된 종목 데이터를 분석하여 투자 판단을 내립니다."""
    print(f"--- [AI Decision Step] Analyzing {stock_name} ---")
    
    # 사용 가능한 모델 확인 및 선택 (flash-latest 선호)
    model_name = 'models/gemini-flash-latest'
    print(f"[System] Selected model: {model_name}")
    
    try:
        model = genai.GenerativeModel(model_name)
    except:
        model = genai.GenerativeModel('models/gemini-pro-latest') # fallback
    
    prompt = f"""
    당신은 전문 주식 트레이더입니다. 아래 데이터를 분석하여 [BUY, SELL, HOLD] 중 하나를 결정하고 이유를 설명하세요.
    응답은 반드시 JSON 형식으로 하세요. (예: {{"decision": "BUY", "reason": "...", "quantity": 1}})

    - 종목명: {stock_name}
    - 현재가: {current_price}원
    - 등락률: {change_rate}%
    - 현재 잔고(예수금): {balance}원
    """
    
    print("[System] Sending request to Gemini AI... (Please wait)")
    response = model.generate_content(prompt)
    
    try:
        # JSON 부분만 추출
        result_text = response.text.strip().replace('```json', '').replace('```', '')
        decision = json.loads(result_text)
        print(f"[Gemini] Analysis complete. Result: {decision.get('decision')}")
        return decision
    except Exception as e:
        print(f"[Error] Failed to parse AI response: {str(e)}")
        return {"decision": "HOLD", "reason": f"AI 분석 오류: {str(e)}", "quantity": 0}

if __name__ == "__main__":
    # 테스트 데이터
    sample_decision = get_trading_decision("Samsung", "199400", "-0.55", "500000000")
    print("\n[Gemini AI Trading Decision Result]")
    print(f"Decision: {sample_decision.get('decision')}")
    print(f"Reason: {sample_decision.get('reason')}")
    print(f"Quantity: {sample_decision.get('quantity')} shares")
