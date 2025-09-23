from __future__ import print_function
from bs4 import BeautifulSoup
import os.path
from config import TOKENDEEPSEEK , TOKENGEMINI
import requests
import json
from telegram.constants import ParseMode
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json;
from config import SHEET_CALENDAR_ID , RANGE_NAME , CALENDAR_ID , SHEET_PROJECT_NAME
from datetime import datetime, timedelta

from google import genai

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes , ConversationHandler



PROJECT_NAME_RANGE="Talent!C"

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/calendar'
          ]

role_map = {
    "TL oGT Sales": "V",
    "TL B2B MKT": "C",
    "TL  Leadgen&CX": "Y"
}

# Головне меню
main_menu = [
    ["xray"],
    ["проєкти"],
    ["постик"],
    ["рм календар"]
]

menu_city = [
    ["Тернопіль", "Рівне"],
    ["назад"]
]

menu_projects = [
    ["Телент", "Тічер"],
    ["назад"]
]

city_name = ""
CHOOSING , CHOOSING_CYTI = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Привіт , як твій день ? , з чого почнемо сьогодні?",
        reply_markup=ReplyKeyboardMarkup(main_menu, one_time_keyboard=False)
    )
    return CHOOSING

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    if "choice" in user_data:
        del user_data["choice"]

    user_data.clear()
    return ConversationHandler.END

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Що вибереш?" ,
        reply_markup=ReplyKeyboardMarkup(main_menu, one_time_keyboard=True)
    )

async def xray(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Оберіть регіон" ,
        reply_markup=ReplyKeyboardMarkup(menu_city, one_time_keyboard=True)
    )

    return CHOOSING


async def city_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global city_name

    city_name = update.message.text
    context.user_data["city_name"] = city_name
    print(city_name)
    await update.message.reply_text(f"Вибране місто: {city_name}?Який ваш X-ray запит?")

    return CHOOSING_CYTI



async def x_raychik(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    x_request = update.message.text
    context.user_data["x_request"] = x_request
    print(x_request)
    text = f"Згенеруй тільки робоче посилання в url кодуванні,як в Google x-ray запиту для пошуку  на LinkedIn за даними:  Місто: {city_name} {x_request} Видай посилання єдиним рядком тексту, без жодних додаткових пояснень чи форматування.{x_request},візьми за основу такий формат посилання:(https://www.google.com/search?q=site%3Alinkedin.com%2Fin%2F%20%22%D0%A2%D0%B5%D1%80%D0%BD%D0%BE%D0%BF%D1%96%D0%BB%D1%8C%22%20%22%D0%B1%D1%96%D0%B7%D0%BD%D0%B5%D1%81%20%D0%B0%D0%B4%D0%BC%D1%96%D0%BD%D1%96%D1%81%D1%82%D1%80%D1%83%D0%B2%D0%B0%D0%BD%D0%BD%D1%8F%22%20%22%D0%B0%D0%BD%D0%B3%D0%BB%D1%96%D0%B9%D1%81%D1%8C%D0%BA%D0%B0%20B1%22)"
    print(text)

    client = genai.Client(api_key=TOKENGEMINI)

    response = client.models.generate_content(
        model = "models/gemini-2.5-pro" ,
        contents = text
    )
    #bot.send_message(chat_id = update.message.chat_id, text = "<a href='https://www.google.com/'>Google</a>", parse_mode = ParseMode.HTML)
    reply=response.text
    print(type(reply))
    print(f"<a href='{response.text}")
    await update.message.reply_text(text = f"<a href='{response.text}'>X-ray</a>", parse_mode = ParseMode.HTML)
    print(response.text)


async def project (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Який тип проєкту?",
        reply_markup=ReplyKeyboardMarkup(menu_projects, one_time_keyboard=False)
    )


async def talent (update: Update, context: ContextTypes.DEFAULT_TYPE):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())

    service = build("sheets", "v4", credentials=creds)

    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=SHEET_PROJECT_NAME, range=PROJECT_NAME_RANGE)
        .execute()
    )
    values = result.get("values", [])

    for row in values:
      # Print columns A and E, which correspond to indices 0 and 4.
      print(f"{row[6]}, {row[4]}")




async def teacher(update: Update, context: ContextTypes.DEFAULT_TYPE):

    pass



async def rm_calendar():

    filename = "data.json"
    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SHEET_CALENDAR_ID,
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
        


