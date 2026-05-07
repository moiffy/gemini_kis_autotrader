import requests
import json

# 한국투자증권 실배전/모의투자 환경 설정
# URL_BASE = "https://openapi.koreainvestment.com:9443"  # 실전투자용 (Real)
URL_BASE = "https://openapivts.koreainvestment.com:29443" # 모의투자용 (Simulation)

def get_access_token(app_key, app_secret):
    """지정된 App Key와 Secret으로 Access Token을 발급받습니다."""
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": app_key,
        "appsecret": app_secret
    }
    path = "oauth2/tokenP"
    url = f"{URL_BASE}/{path}"
    
    res = requests.post(url, headers=headers, data=json.dumps(body))
    
    if res.status_code == 200:
        return res.json().get('access_token')
    else:
        print(f"Error: {res.status_code}, {res.text}")
        return None

if __name__ == "__main__":
    # 아래 정보를 한국투자증권 앱/웹사이트에서 발급받아 입력해야 합니다!
    APP_KEY = "****"
    APP_SECRET = "****"
    
    token = get_access_token(APP_KEY, APP_SECRET)
    if token:
        print(f"Auth Success! Access Token: {token[:10]}...")
    else:
        print("Auth Failed! Please check your Key and Secret.")
