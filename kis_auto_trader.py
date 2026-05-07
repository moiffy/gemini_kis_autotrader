import os
import requests
import json
import time
from google import genai
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

# [설정] KIS API 정보 (모의투자 전용) ✅
APP_KEY = os.environ.get("KIS_APP_KEY", "")
APP_SECRET = os.environ.get("KIS_APP_SECRET", "")
URL_BASE = os.environ.get("KIS_URL_BASE", "https://openapivts.koreainvestment.com:29443") # 모의투자 URL
ACC_NO = os.environ.get("KIS_ACC_NO", "")
ACC_CODE = os.environ.get("KIS_ACC_CODE", "01")

# [설정] Gemini API 정보 ✅
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

def get_access_token():
    headers = {"content-type": "application/json"}
    body = {"grant_type": "client_credentials", "appkey": APP_KEY, "appsecret": APP_SECRET}
    res = requests.post(f"{URL_BASE}/oauth2/tokenP", headers=headers, data=json.dumps(body))
    return res.json().get('access_token')

def get_current_price(token, stock_code):
    yf_code = f"{stock_code}.KS"
    try:
        ticker = yf.Ticker(yf_code)
        data_2d = ticker.history(period='5d')
        if data_2d.empty: return {}
        prpr = data_2d['Close'].iloc[-1]
        if len(data_2d) > 1:
            prev_close = data_2d['Close'].iloc[-2]
            change_rate = ((prpr - prev_close) / prev_close) * 100
        else:
            change_rate = 0.0
        return {"stck_prpr": str(int(prpr)), "prdy_ctrt": f"{change_rate:.2f}"}
    except Exception as e:
        return {}

def buy_stock(token, stock_code, quantity):
    """주식 매수 주문 (모의투자 전용) ✅"""
    headers = {
        "Content-Type": "application/json", "Authorization": f"Bearer {token}",
        "appkey": APP_KEY, "appsecret": APP_SECRET, "tr_id": "VTTC0802U" # 모의투자 매수 ID
    }
    body = {
        "CANO": ACC_NO, "ACNT_PRDT_CD": ACC_CODE, "PDNO": stock_code,
        "ORD_DVSN": "01", "ORD_QTY": str(quantity), "ORD_UNPR": "0" # 시장가 주문
    }
    res = requests.post(f"{URL_BASE}/uapi/domestic-stock/v1/trading/order-cash", headers=headers, data=json.dumps(body))
    return res.json()

def get_ohlcv(token, stock_code):
    """최근 10일치 OHLCV 데이터를 Yahoo Finance에서 가져옵니다. ✅"""
    yf_code = f"{stock_code}.KS"
    try:
        ticker = yf.Ticker(yf_code)
        data = ticker.history(period='10d')
        if data.empty: return "OHLCV Data Unavailable"
        
        summary = ""
        for date, row in data.iterrows():
            summary += f"[Date:{date.strftime('%Y-%m-%d')}] Close:{int(row['Close'])} High:{int(row['High'])} Low:{int(row['Low'])} Vol:{int(row['Volume'])}\n"
        return summary
    except:
        return "OHLCV Data Unavailable"

def ai_decision(stock_name, price_info, ohlcv_data):
    """Gemini AI에게 OHLCV를 포함한 심층 매매 판단 요청 ✅"""
    prompt = f"""
    You are an expert stock trader. Analyze the following data and decide whether to BUY, SELL, or HOLD.
    Stock: {stock_name}
    Current Price: {price_info.get('stck_prpr')} KRW
    Daily Change: {price_info.get('prdy_ctrt')}%
    
    Recent 10 Days OHLCV (Close, High, Low, Volume):
    {ohlcv_data}
    
    Provide your decision and a short, one-sentence rationale in Korean.
    Answer ONLY in the following valid JSON format without any markdown type wrappers:
    {{"decision": "BUY", "reason": "한글로 쓰여진 짧은 매매 사유", "qty": 1}}
    """
    raw_response = ""
    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        raw_response = response.text
        # JSON 포맷 안전 추출
        clean_text = response.text.strip()
        if clean_text.startswith("```json"): clean_text = clean_text[7:]
        if clean_text.endswith("```"): clean_text = clean_text[:-3]
        return json.loads(clean_text)
    except Exception as e:
        print(f"[Error: {str(e)}] Raw response: {raw_response}", flush=True)
        return {"decision": "HOLD", "reason": "Failed to analyze data", "qty": 0}

def main():
    print("--- [Auto Trader Simulation Started (OHLCV Integrated)] ---", flush=True)
    token = get_access_token()
    stocks = {
        "Samsung (삼성전자)": "005930", 
        "SK Hynix (SK하이닉스)": "000660",
        "Hyundai (현대차)": "005380",
        "KIA (기아)": "000270",
        "Naver (네이버)": "035420",
        "Kakao (카카오)": "035720",
        "Celltrion (셀트리온)": "068270",
        "POSCO (포스코홀딩스)": "005490",
        "LG Energy (LG엔솔)": "373220",
        "KB Financial (KB금융)": "105560"
    } # 10대 우량주 초단타 감시 목록
    
    print("\n[System] 야후 파이낸스 차단 방지를 위해 10일치 데이터를 메모리에 캐싱합니다...", flush=True)
    ohlcv_cache = {}
    for name, code in stocks.items():
        ohlcv_cache[name] = get_ohlcv(token, code)
        time.sleep(1)
        
    while True:
        for name, code in stocks.items():
            print(f"\n[System] Checking {name}...", flush=True)
            price_info = get_current_price(token, code)
            ohlcv = ohlcv_cache.get(name, "OHLCV Data Unavailable") # 매번 불러오지 않고 캐시된 데이터 활용
            
            decision = ai_decision(name, price_info, ohlcv)
            print(f"[AI Decision] {name} -> {decision.get('decision')}", flush=True)
            print(f"  -> Reason: {decision.get('reason', 'None')}", flush=True)
            
            if decision.get('decision') == "BUY":
                print(f"[Action] Purchasing {decision.get('qty')} shares of {name}...", flush=True)
                order_res = buy_stock(token, code, decision.get('qty'))
                print(f"[Order Result] {order_res.get('msg1')}", flush=True)
            
            time.sleep(6) # 종목 간 API 과부하 방지 (Gemini 15 RPM 제한 회피) 6초 대기
        
        print("\n--- [1사이클 종료] 안전한 API 호출을 위해 2분 30초 대기합니다... ---", flush=True)
        time.sleep(150) # 150초 대기 (Gemini 무과금 및 Yahoo Finance 차단 완벽 방지)

if __name__ == "__main__":
    main()
