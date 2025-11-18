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

from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
import time

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes , ConversationHandler


PROJECT_NAME_RANGE="Talent!C"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    'https://www.googleapis.com/auth/calendar'
          ]

creds = None
if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        pass
        #creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
    with open("token.json", "w") as token:
        token.write(creds.to_json())

service = build("sheets", "v4", credentials=creds)
sheet = service.spreadsheets()

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
    ["рМкалендар"]
]

menu_city = [
    ["Тернопіль", "Рівне"],
    ["назад"]
]

menu_projects = [
    ["Телент", "Тічер"],
    ["назад"]
]

projectA_doing = [
    ["Додати", "Видалити"],
    ["назад"]
]

projectA_part_lc2lc = [
    ["Фокусні" , "Партнери"],
    ["назад"]
]
menu_postik = [
    ["назад"]
]

city_name = ""
CHOOSING , CHOOSING_CYTI , GET_LINK , POST = range(4)


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
    await update.message.reply_text(f"Вибране місто: {city_name}?Який ваш X-ray запит? Для прикладу 'навчались в університеті тернополя , 18-30 років , викладач англійської мови'")

    return CHOOSING_CYTI



async def x_raychik(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    x_request = update.message.text
    context.user_data["x_request"] = x_request
    print(x_request)
    sent_message = await context.bot.send_message(chat_id=update.message.chat_id, text="Генерація запиту...")
    message_to_delete_id = sent_message.message_id

    text = f'Згенеруй тільки робоче посилання в url кодуванні,як в Google x-ray запиту для пошуку  на LinkedIn за даними:  Місто: {city_name} {x_request} Видай посилання єдиним рядком тексту, без жодних додаткових пояснень чи форматування.{x_request},візьми за основу такий формат посилання:(https://www.google.com/search?q=site%3Alinkedin.com%2Fin%2F%20%22%D0%A2%D0%B5%D1%80%D0%BD%D0%BE%D0%BF%D1%96%D0%BB%D1%8C%22%20%22%D0%B1%D1%96%D0%B7%D0%BD%D0%B5%D1%81%20%D0%B0%D0%B4%D0%BC%D1%96%D0%BD%D1%96%D1%81%D1%82%D1%80%D1%83%D0%B2%D0%B0%D0%BD%D0%BD%D1%8F%22%20%22%D0%B0%D0%BD%D0%B3%D0%BB%D1%96%D0%B9%D1%81%D1%8C%D0%BA%D0%B0%20B1%22) та такий тип запиту "site:linkedin.com/in ("Тернопіль" OR "Ternopil" OR "Тернопільський університет" OR "Ternopil University") ("викладач англійської" OR "English teacher") ("18..30")'
    print(text)

    client = genai.Client(api_key=TOKENGEMINI)

    response = client.models.generate_content(
        model = "models/gemini-2.5-pro" ,
        contents = text
    )
    await context.bot.deleteMessage(message_id=message_to_delete_id, chat_id=update.message.chat_id)
    print(response.text)
    print(f"<a href='{response.text}")
    await update.message.reply_text(text = f"<a href='{response.text}'>Ваш X-ray запит</a>", parse_mode = ParseMode.HTML)
    print(response.text)
    await update.message.reply_text(
        "Що далі?",
        reply_markup=ReplyKeyboardMarkup(main_menu, one_time_keyboard=True)
    )
    return 0

async def post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        f"Надай мені посилання на проект: ",
        reply_markup=ReplyKeyboardMarkup(menu_postik, one_time_keyboard=True)
    )
    postik
    return POST

async def postik(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    req_for_prompt=update.message.text
    client = genai.Client(api_key=TOKENGEMINI)
    with open('prompt.txt', 'r', encoding='utf-8') as file:
        file_content = file.read()

    response = client.models.generate_content(
        model="models/gemini-2.5-pro",
        contents=f"Привіт,ось посилання на проект : {req_for_prompt}. Збери дані з цього сайту та надай мені відповідь у такому чіткому форматі:{file_content} (надай мені тільки сам результат без лишнього тексту та лапок)",
    )
    project_text= response.text
    print(project_text)
    response = client.models.generate_content(
        model="models/gemini-2.5-pro",
        contents=f"Поверни мені тільки назву міста і країну з цих даних: {project_text}(тільки результат без будь якого зайвого тексту)",
    )
    place=response.text
    print(place)

    response = client.models.generate_content(
        model="models/gemini-2.5-pro",
        contents=f"",
    )

    # Команда для відправки фото за URL
    await context.bot.send_photo(chat_id=update.message.chat_id, image="image_stream")
    return 0


async def project (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Який тип проєкту?",
        reply_markup=ReplyKeyboardMarkup(menu_projects, one_time_keyboard=False)
    )


async def talent (update: Update, context: ContextTypes.DEFAULT_TYPE):

    result = sheet.values().get(
        spreadsheetId=SHEET_PROJECT_NAME,
        range="Talent!C5:C"
    ).execute()

    values = result.get("values", [])

    text = ""
    empty_count = 0
    line_number = 1  # для нумерації реальних рядків, починаємо після першого

    for idx, row in enumerate(values):
        if not row or not row[0].strip():  # порожня клітинка
            empty_count += 1
            if empty_count == 2:
                text += "партнери\n"
                print("партнери")
            elif empty_count == 3:
                break
            continue

        # перша клітинка (C5) без номера
        if idx == 0:
            text += f"{row[0]}\n"
            print(row[0])
        else:
            text += f"{line_number}. {row[0]}\n"
            print(f"{line_number}. {row[0]}")
            line_number += 1

    await update.message.reply_text(
        text or "Що з цим робити?",
        reply_markup=ReplyKeyboardMarkup(projectA_doing, one_time_keyboard=False)
    )

    return CHOOSING

async def A_choose_where (update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "куди саме?",
        reply_markup=ReplyKeyboardMarkup(projectA_part_lc2lc, one_time_keyboard=True)
    )

    return CHOOSING



async def Focus_A (update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Вставте лінку яку хочете додати",
    )

    return GET_LINK

async def normalize_value(value):
    # Якщо список -> перетворюємо в рядок
    if isinstance(value, list):
        return ", ".join(map(str, value))
    return value

async def add_to_table (update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text
    context.user_data["url"] = url
    print(url)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")

        # --- Заголовок ---
        title_element = await page.wait_for_selector("h3.font-bold.text-3xl.flex-1")
        title = await title_element.inner_text()
        print("Title:")
        print(title)
        print()

        # --- Періоди (чекаємо стабільно) ---
        print("Periods:")

        await page.wait_for_selector("div.gradient-container_gradient-box__HgOQI")

        for attempt in range(5):
            period_blocks = await page.query_selector_all("div.gradient-container_gradient-box__HgOQI")
            results = []
            for block in period_blocks:
                info_container = await block.query_selector("div[class*='flex-col'][class*='w-full']")
                if info_container:
                    period_div = await info_container.query_selector("div:nth-child(1)")
                    slots_div = await info_container.query_selector("div:nth-child(2)")
                    period = (await period_div.inner_text()).strip() if period_div else None
                    slots = (await slots_div.inner_text()).strip() if slots_div else None
                    if period and slots:
                        results.append((period, slots))
            if results:
                for period, slots in results:
                    print(period)
                    print(slots)
                break
            else:
                await asyncio.sleep(1)  # заміна time.sleep
        print()

        # --- Роль ---
        role_element = await page.query_selector("div.text-base")
        role_text = (await role_element.inner_text()).strip() if role_element else None
        print("Role description:")
        print(role_text)
        print()

        # --- Вимоги ---
        required_blocks = await page.query_selector_all(
            "div[class*='eligibility-tag']:has(span:text('(Required)'))"
        )
        required_items = []
        for block in required_blocks:
            spans = await block.query_selector_all("span")
            if len(spans) >= 2:
                name = (await spans[0].inner_text()).strip()
                required_items.append(name)
        print("Required:")
        for item in sorted(set(required_items)):
            print(item)
        print()

        # --- Скіли ---
        skill_blocks = await page.query_selector_all("div[class*='eligibility-tag']")
        skills = []
        for block in skill_blocks:
            spans = await block.query_selector_all("span")
            if spans:
                skill_name = (await spans[0].inner_text()).strip()
                skills.append(skill_name)
        print("Skills:")
        for skill in sorted(set(skills)):
            print(skill)
        print()

        # --- Зарплата ---
        salary_el = await page.query_selector("div:has(svg.fa-wallet) span.font-bold")
        salary = (await salary_el.inner_text()).strip() if salary_el else "Not specified"
        print("Salary:")
        print(salary)
        print()

        # --- Логістика ---
        logistics_blocks = await page.query_selector_all("div[class*='logistics_']")
        benefits = {"accommodation": False, "food": False, "transport": False}

        for block in logistics_blocks:
            log_title_el = await block.query_selector("span.font-bold.text-base")
            desc_el = await block.query_selector("div.flex.flex-col div")
            if not log_title_el or not desc_el:
                continue

            log_title = (await log_title_el.inner_text()).strip().lower()
            desc = (await desc_el.inner_text()).strip().lower()

            if "accommodation" in log_title:
                benefits["accommodation"] = "provided" in desc or "will be" in desc
            if "food" in log_title:
                benefits["food"] = "provided" in desc or "meal" in desc
            if "transport" in log_title or "travel" in desc or "flight" in desc:
                benefits["transport"] = True

        print("Logistics:")
        for key in ["accommodation", "food", "transport"]:
            status = "Yes" if benefits[key] else "No"
            print(f"{key.capitalize()}: {status}")

        await browser.close()

    result = sheet.values().get(
        spreadsheetId=SHEET_PROJECT_NAME,
        range="Talent!A:A"
    ).execute()

    values = result.get("values", [])

    Partners_row = None

    # Вивести значення листа
    '''spreadsheet = sheet.get(spreadsheetId=SHEET_PROJECT_NAME).execute()
    for s in spreadsheet["sheets"]:
        print(s["properties"]["title"], s["properties"]["sheetId"])
'''
    for i, row in enumerate(values, start=1):
        if row and row[0].strip().lower() == "partners":
            Partners_row = i
            break

    if Partners_row is not None:
        # Вставка нового рядка
        sheet.batchUpdate(
            spreadsheetId=SHEET_PROJECT_NAME,
            body={
                "requests": [
                    {
                        "insertDimension": {
                            "range": {
                                "sheetId": 1457578285,
                                "dimension": "ROWS",
                                "startIndex": Partners_row - 1,
                                "endIndex": Partners_row,
                            },
                            "inheritFromBefore": False,
                        }
                    }
                ]
            },
        ).execute()

        row_values = [
            await normalize_value(slots),  # B
            await normalize_value(title),  # C
            await normalize_value(period),  # D
            await normalize_value(url),  # E
            await normalize_value(role_text),  # F
            await normalize_value(item),  # G
            await normalize_value(skills),  # H (завжди список → тут стане рядок)
            await normalize_value("TRUE" if benefits["accommodation"] else "FALSE"),  # I
            await normalize_value("TRUE" if benefits["food"] else "FALSE"),  # J
            await normalize_value("TRUE" if benefits["transport"] else "FALSE"),  # K
            await normalize_value(salary)  # L
        ]

        # Запис значень
        sheet.values().update(
            spreadsheetId=SHEET_PROJECT_NAME,
            range=f"Talent!B{Partners_row}:L{Partners_row}",
            valueInputOption="USER_ENTERED",
            body={"values": [row_values]},
        ).execute()

        # Форматування чекбоксів у колонках I, J, K
        sheet.batchUpdate(
            spreadsheetId=SHEET_PROJECT_NAME,
            body={
                "requests": [
                    {
                        "setDataValidation": {
                            "range": {
                                "sheetId": 1457578285,
                                "startRowIndex": Partners_row - 1,
                                "endRowIndex": Partners_row,
                                "startColumnIndex": 8,  # колонка I (0-індексація)
                                "endColumnIndex": 11,  # до K включно
                            },
                            "rule": {
                                "condition": {"type": "BOOLEAN"},
                                "inputMessage": "Познач ✓ або залиш порожнім",
                                "strict": True,
                                "showCustomUi": True,
                            },
                        }
                    }
                ]
            },
        ).execute()

        print(f"✅ У рядок {Partners_row} додано значення у B–L")
    else:
        print("❌ 'Partners' не знайдено в колонці A")

    await update.message.reply_text(
        "Готово",
        reply_markup=ReplyKeyboardMarkup(projectA_part_lc2lc, one_time_keyboard=False))

    return CHOOSING


async def teacher(update: Update, context: ContextTypes.DEFAULT_TYPE):

    pass



async def rm_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):

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
        

    return CHOOSING
