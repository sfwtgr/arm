import os
import requests
import yfinance as yf
import google.generativeai as genai

# 1. ตั้งค่า Gemini
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

def get_analysis(name, price):
    try:
        # ใช้โมเดลที่เสถียรที่สุดในปัจจุบัน
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"วิเคราะห์หุ้น {name} ราคาปัจจุบัน {price} USD สรุปสั้นๆ 1 บรรทัดภาษาไทย"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        import google.generativeai as pkg
        # บรรทัดนี้จะช่วยเช็คเลขเวอร์ชันใน LINE ครับ
        return f"ติดปัญหา: {str(e)[:30]} (Ver: {pkg.__version__})"

def main():
    line_token = os.environ.get('LINE_TOKEN', '').strip()
    stocks = ["NVDA", "AAPL", "TSLA"]
    report = "🚀 [รายงานหุ้น AI - ระบบคอมพิวเตอร์]\n"
    
    for sym in stocks:
        try:
            ticker = yf.Ticker(sym)
            price = ticker.info.get('currentPrice', 'N/A')
            analysis = get_analysis(sym, price)
            report += f"\n📌 {sym}: {price} USD\n💡 {analysis}\n"
        except:
            report += f"\n📌 {sym}: ดึงข้อมูลไม่สำเร็จ\n"

    # 2. ส่งเข้า LINE (Broadcast)
    url = 'https://api.line.me/v2/bot/message/broadcast'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {line_token}'
    }
    payload = {'messages': [{'type': 'text', 'text': report}]}
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    main()
