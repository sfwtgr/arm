import os
import time
import requests
import yfinance as yf
import google.generativeai as genai

genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

def get_analysis(name, price):
    for attempt in range(3):  # ลองใหม่สูงสุด 3 ครั้ง
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            prompt = f"วิเคราะห์หุ้น {name} ราคา {price} USD สรุปสั้นๆ 1 บรรทัดภาษาไทย"
            response = model.generate_content(
                prompt,
                request_options={"timeout": 30}  # timeout 30 วินาที
            )
            return response.text.strip()
        except Exception as e:
            print(f"⚠️ {name} attempt {attempt+1} failed: {str(e)[:60]}")
            if attempt < 2:
                time.sleep(10)  # รอ 10 วินาทีก่อนลองใหม่
    return "วิเคราะห์ไม่สำเร็จ (server ไม่ตอบ)"

def send_line_message(token, message):
    if not token:
        print("❌ ไม่พบ LINE_TOKEN")
        return False
    url = 'https://api.line.me/v2/bot/message/broadcast'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    payload = {'messages': [{'type': 'text', 'text': message}]}
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        res.raise_for_status()
        print("✅ ส่ง LINE สำเร็จ")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ ส่ง LINE ไม่สำเร็จ: {e}")
        return False

def main():
    # เช็ค API Key ก่อนเริ่ม
    api_key = os.environ.get('GEMINI_API_KEY')
    line_token = os.environ.get('LINE_TOKEN', '').strip()
    print("GEMINI KEY:", "พบแล้ว ✅" if api_key else "ไม่พบ ❌")
    print("LINE TOKEN:", "พบแล้ว ✅" if line_token else "ไม่พบ ❌")

    stocks = ["NVDA", "AAPL", "TSLA"]
    report = "🚀 [รายงานหุ้น AI - ระบบคอมพิวเตอร์]\n"

    for sym in stocks:
        try:
            info = yf.Ticker(sym).info
            price = info.get('currentPrice') or info.get('regularMarketPrice', 'N/A')
            analysis = get_analysis(sym, price)
            report += f"\n📌 {sym}: {price} USD\n💡 {analysis}\n"
            time.sleep(5)  # หน่วงระหว่างแต่ละหุ้นเพื่อไม่ให้เกิน quota
        except Exception as e:
            print(f"❌ ดึงข้อมูล {sym} ไม่สำเร็จ: {e}")
            report += f"\n📌 {sym}: ดึงข้อมูลไม่สำเร็จ\n"

    print(report)
    send_line_message(line_token, report)

if __name__ == "__main__":
    main()
