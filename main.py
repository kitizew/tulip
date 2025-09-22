from codeToRm import CHOOSING
from config import TOKENTELEGRAM
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

from function import *




'''
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    await update.message.reply_text("Головне меню:", reply_markup=reply_markup)
'''










'''
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    match text:
        case "x-ray запит":
            await update.message.reply_text("Регіон?", reply_markup=ReplyKeyboardMarkup(menu_project, resize_keyboard=True , one_time_keyboard=True))
        case "Тернопіль":
            await x_ray_request(text)
        case "Рівне":
            await x_ray_request(text , update)

            await update.message.reply_text("Чувак,введи шо ти хочеш ")
            #t=update.message.text()
            #print(t)
            print(x_ray_request(text))


        case "проєкти":
            #await update.message.reply_text("веном")
            await project()


        case "":
            await


        case "рм календар":
            await rm_calendar()


        case "назад":
            await update.message.reply_text("Повертаємось", reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True))


        case _:
            await update.message.reply_text("Я не знаю такої кнопки 🤔")
'''
def main():
    application = Application.builder().token(TOKENTELEGRAM).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start)
            #CommandHandler("рм календар", await rm_calendar())
                      ],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^(xray)$"), xray),
                MessageHandler(filters.Regex("^(Тернопіль)$"), ternopil_choice ),

            ]

        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
    )
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)




if __name__ == "__main__":
    main()