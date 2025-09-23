from codeToRm import CHOOSING
from config import TOKENTELEGRAM
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

from function import *

def main():
    application = Application.builder().token(TOKENTELEGRAM).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start)
            #CommandHandler("рм календар", await rm_calendar())
                      ],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^(назад)$"), back),
                MessageHandler(filters.Regex("^(xray)$"), xray),
                MessageHandler(filters.Regex("^(Тернопіль|Рівне)$"), city_choice ),
                MessageHandler(filters.Regex("^(проєкти)$"), project),
                MessageHandler(filters.Regex("^(Телент)$"), talent),
                #MessageHandler(filters.Regex("^(Тічер)$"), teacher),

            ],
            CHOOSING_CYTI: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, x_raychik)
            ]

        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
    )
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)




if __name__ == "__main__":
    main()