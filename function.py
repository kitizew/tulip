from __future__ import print_function
from bs4 import BeautifulSoup
import os.path
from config import TOKENDEEPSEEK
import requests
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json;
from config import SPREADSHEET_ID , RANGE_NAME , CALENDAR_ID
from datetime import datetime, timedelta

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/calendar'
          ]

role_map = {
    "TL oGT Sales": "V",
    "TL B2B MKT": "C",
    "TL  Leadgen&CX": "Y"
}

async def x_ray_request(text , update):

    #aboba = update.message.reply_text("абоба")

    #await update.message.reply_text("sdfastew")
    #context.user_data["choice"] = text
    print(text)
    aboba = await update.message.reply_text("гойда")
    print(aboba)

    #text = Update.message.text
    api_key = TOKENDEEPSEEK
    text = f"w {aboba}"

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": "deepseek/deepseek-chat-v3.1:free",
            "messages": [
                {"role": "user", "content": text }
            ],
        })
    )

    result = response.json()

    if "choices" in result:
        print(result["choices"][0]["message"]["content"])
    else:
        print("Помилка від API:", result)


'''async def projects (text):'''


'''async def rm_calendar():

    filename = "data.json"

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()

    rows = result.get('values', [])
    keywords = ['TL  Leadgen&CX', 'TL oGT Sales', 'TL B2B MKT']

    extracted_rows = []

    for row in rows:
        for i, cell in enumerate(row):
            if cell in keywords:
                # беремо попередній рядок як текст, сам TL, та наступну клітинку як дату
                text = row[i - 1] if i - 1 >= 0 else ""
                tl = cell
                date = row[i + 1] if i + 1 < len(row) else ""
                extracted_rows.append([text, tl, date])

    # Записуємо у JSON
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(extracted_rows, f, ensure_ascii=False, indent=2)




    """Нормалізує всі дати у файлі JSON до формату YYYY-MM-DD"""
    formats = ["%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%y"]

    def normalize_date(date_str: str) -> str:
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        return date_str  # якщо формат невідомий — залишаємо як є

    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    for row in data:
        if len(row) >= 3:
            row[2] = normalize_date(row[2])

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Авторизація в Google Calendar API
    service = build('calendar', 'v3', credentials=creds)

    # Додаємо події
    for task in data:
        title, role, date = task
        letter = role_map.get(role, "?")
        event = {
            "summary": f"{letter}.Action {title}",  # Назва події
            "start": {"date": date},  # початок події (весь день)
            "end": {"date": date},  # кінець події (той самий день)
        }

        created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        print(f"✅ Додано подію: {created_event['summary']} на {date}")
        
        '''

