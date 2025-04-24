from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler

TELEGRAM_TOKEN = "7210822073:AAFM7PAj5D9PEJrvwArF8rSaU4FqsyT-3ns"
WEB_APP_URL = "https://shop-miniapp.onrender.com"

async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton(
            "Открыть приложение",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )]
    ]
    await update.message.reply_text(
        "Добро пожаловать!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.run_polling()
