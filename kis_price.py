import requests
import json

# 인증 정보
APP_KEY = "****"
APP_SECRET = "****"
URL_BASE = "https://openapivts.koreainvestment.com:29443" # 모의투자

def get_access_token():
    headers = {"content-type": "application/json"}
    body = {"grant_type": "client_credentials", "appkey": APP_KEY, "appsecret": APP_SECRET}
    res = requests.post(f"{URL_BASE}/oauth2/tokenP", headers=headers, data=json.dumps(body))
    return res.json().get('access_token')

def get_current_price(access_token, stock_code):
    """지정된 종목의 현재가를 조회합니다. ✅"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHKST01010100" # 주식현재가 시세 조회용 (국내주식)
    }
    
    params = {
        "FID_COND_MRKT_DIV_CODE": "J", # 주식
        "FID_INPUT_ISCD": stock_code   # 종목코드
    }
    
    url = f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-price"
    res = requests.get(url, headers=headers, params=params)
    return res.json()

if __name__ == "__main__":
    TOKEN = get_access_token()
    if TOKEN:
        # 관심 종목 리스트 (영문 이름으로 출력하여 인코딩 문제 방지)
        stocks = {
            "Samsung": "005930",
            "SK Hynix": "000660",
            "Woori Tech": "032820",
            "KoAct ETF": "466940"
        }
        
        print(f"{'Stock':<12} | {'Price':>10} | {'Change':>8}")
        print("-" * 38)
        
        for name, code in stocks.items():
            data = get_current_price(TOKEN, code)
            if data.get('rt_cd') == '0':
                price_info = data.get('output', {})
                price = format(int(price_info.get('stck_prpr', 0)), ',')
                rate = price_info.get('prdy_ctrt', '0.00')
                print(f"{name:<12} | {price:>10} | {rate:>7}%")
            else:
                print(f"{name:<12} | Error: {data.get('msg1')}")
