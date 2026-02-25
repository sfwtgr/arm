import os
import time  # ← เพิ่มตรงนี้
import requests
import yfinance as yf
import google.generativeai as genai

genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

def get_analysis(name, price):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"วิเคราะห์หุ้น {name} ราคา {price} USD สรุปสั้นๆ 1 บรรทัดภาษาไทย"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"วิเคราะห์ไม่สำเร็จ: {str(e)[:50]}"

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
    line_token = os.environ.get('LINE_TOKEN', '').strip()
    stocks = ["NVDA", "AAPL", "TSLA"]
    report = "🚀 [รายงานหุ้น AI - ระบบคอมพิวเตอร์]\n"

    for sym in stocks:
        try:
            info = yf.Ticker(sym).info
            price = info.get('currentPrice') or info.get('regularMarketPrice', 'N/A')
            analysis = get_analysis(sym, price)
            report += f"\n📌 {sym}: {price} USD\n💡 {analysis}\n"
            time.sleep(5)  # ← เพิ่มตรงนี้
        except Exception as e:
            print(f"❌ ดึงข้อมูล {sym} ไม่สำเร็จ: {e}")
            report += f"\n📌 {sym}: ดึงข้อมูลไม่สำเร็จ\n"

    print(report)
    send_line_message(line_token, report)

if __name__ == "__main__":
    main()
