import requests
import json

APP_KEY = "****"
APP_SECRET = "****"
URL_BASE = "https://openapivts.koreainvestment.com:29443"

def test_api():
    # 1. 토큰 발급
    headers = {"content-type": "application/json"}
    body = {"grant_type": "client_credentials", "appkey": APP_KEY, "appsecret": APP_SECRET}
    res = requests.post(f"{URL_BASE}/oauth2/tokenP", headers=headers, data=json.dumps(body))
    token = res.json().get('access_token')
    
    # 2. 시세 조회 테스트
    headers_price = {
        "Content-Type": "application/json", "Authorization": f"Bearer {token}",
        "appkey": APP_KEY, "appsecret": APP_SECRET, "tr_id": "FHKST01010100"
    }
    params_price = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": "005930"}
    res_price = requests.get(f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-price", headers=headers_price, params=params_price)
    
    print("=== Price API Response ===")
    print(res_price.json())
    
    # 3. OHLCV 조회 테스트
    headers_ohlcv = headers_price.copy()
    headers_ohlcv["tr_id"] = "FHKST01010400"
    params_ohlcv = {
        "FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": "005930",
        "FID_PERIOD_DIV_CODE": "D", "FID_ORG_ADJ_PRC": "0"
    }
    res_ohlcv = requests.get(f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-daily-price", headers=headers_ohlcv, params=params_ohlcv)
    print("\n=== OHLCV API Response ===")
    print(res_ohlcv.json())

if __name__ == "__main__":
    test_api()
