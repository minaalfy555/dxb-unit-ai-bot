from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

TOKEN = "8720630364:AAFuXV5h_IgzNEGUZbVFvTzQSgWdnqpoBOA"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحبًا بك في DXB Unit AI\n"
        "Welcome to DXB Unit AI\n\n"
        "أرسل رابط الإعلان أو صورة العقار لتحليلها.\n"
        "Send a property link or image to analyze it."
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "تم استلام الرسالة.\n"
        "Message received."
    )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, echo))

app.run_polling()
