from codeToRm import CHOOSING
from config import TOKENTELEGRAM
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

from function import *

# Головне меню
main_menu = [
    ["x-ray запит"],
    ["проєкти"],
    [""],
    ["рм календар"]
]

menu_project = [
    ["Тернопіль", "Рівне"],
    ["назад"]
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    await update.message.reply_text("Головне меню:", reply_markup=reply_markup)

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    match text:
        case "x-ray запит":
            await update.message.reply_text("Регіон?", reply_markup=ReplyKeyboardMarkup(menu_project, resize_keyboard=True , one_time_keyboard=True))
        case "Тернопіль":
            '''await x_ray_request(text)'''
        case "Рівне":
            await x_ray_request(text , update)

            '''await update.message.reply_text("Чувак,введи шо ти хочеш ")
            #t=update.message.text()
            #print(t)
            print(x_ray_request(text))'''


        case "проєкти":
            #await update.message.reply_text("веном")
            '''await project()'''


        case "":
            '''await'''


        case "рм календар":
            '''await rm_calendar()'''


        case "назад":
            await update.message.reply_text("Повертаємось", reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True))


        case _:
            await update.message.reply_text("Я не знаю такої кнопки 🤔")

def main():
    app = Application.builder().token(TOKENTELEGRAM).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()


if __name__ == "__main__":
    main()
