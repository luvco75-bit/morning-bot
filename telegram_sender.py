import requests
import streamlit as st

def send_to_telegram(flattened_news):
    token = st.secrets["TELEGRAM_TOKEN"]
    chat_id = st.secrets["TELEGRAM_CHAT_ID"]

    message = "🤖 **자비스 모닝 브리핑**\n\n"
    for item in flattened_news:
        message += f"📌 **[{item['카테고리']}]**\n"
        message += f"제목: {item['제목']}\n"
        message += f"링크: {item['링크']}\n\n"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}

    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except:
        return False
