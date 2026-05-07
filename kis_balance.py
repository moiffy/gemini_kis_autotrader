import requests
import json

# 인증 정보 (이전 단계에서 확인된 값)
APP_KEY = "****"
APP_SECRET = "****"
# URL_BASE = "https://openapi.koreainvestment.com:9443" # 실전
URL_BASE = "https://openapivts.koreainvestment.com:29443" # 모의투자

def get_access_token():
    headers = {"content-type": "application/json"}
    body = {"grant_type": "client_credentials", "appkey": APP_KEY, "appsecret": APP_SECRET}
    res = requests.post(f"{URL_BASE}/oauth2/tokenP", headers=headers, data=json.dumps(body))
    return res.json().get('access_token')

def get_balance(access_token, account_no, account_code):
    """주식 잔고를 조회합니다. ✅"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "VTTC8434R" # 모의투자용 주식잔고조달 ID (실전은 TTTC8434R)
    }
    
    params = {
        "CANO": account_no,         # 계좌번호 앞 8자리
        "ACNT_PRDT_CD": account_code, # 계좌번호 뒤 2자리
        "AFHR_FLPR_YN": "N",
        "OFRT_WTHR_YN": "N",
        "PRCS_DVSN": "01",
        "UNPR_DVSN": "01",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }
    
    url = f"{URL_BASE}/uapi/domestic-stock/v1/trading/inquire-balance"
    res = requests.get(url, headers=headers, params=params)
    return res.json()

if __name__ == "__main__":
    TOKEN = get_access_token()
    if TOKEN:
        ACC_NO = "44282180"
        ACC_CODE = "01"
        
        balance_data = get_balance(TOKEN, ACC_NO, ACC_CODE)
        
        if balance_data.get('rt_cd') == '0':
            print("[Balance Inquiry Result]")
            output = balance_data.get('output2', [])
            if output:
                summary = output[0]
                print(f"Total Evaluation Amount: {summary.get('tot_evlu_amt')} KRW")
                print(f"Deposit Amount: {summary.get('dnca_tot_amt')} KRW")
                print(f"Total Return: {summary.get('evlu_pnl_rt')}%")
            else:
                print("Balance data is empty. (No transaction history found)")
        else:
            print(f"Error occurred: {balance_data.get('msg1')}")
