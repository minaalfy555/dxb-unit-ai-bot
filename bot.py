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
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
import requests
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import io

TOKEN = "YOUR_TOKEN_HERE"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحبًا بك في DXB Unit AI\n"
        "أرسل رابط الإعلان أو صورة العقار لتحليلها."
    )

# -------------------------------
# تحليل الروابط
# -------------------------------
def analyze_link(url):
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.find("h1")
        price = soup.find("span", {"aria-label": "Price"})
        area = soup.find("span", string=lambda x: x and "sqft" in x.lower())

        return (
            f"🏡 **تحليل الرابط**\n\n"
            f"العنوان: {title.text.strip() if title else 'غير متوفر'}\n"
            f"السعر: {price.text.strip() if price else 'غير متوفر'}\n"
            f"المساحة: {area.text.strip() if area else 'غير متوفر'}\n"
        )
    except:
        return "⚠ لا يمكن تحليل الرابط."

# -------------------------------
# تحليل الصور
# -------------------------------
def analyze_image(file_bytes):
    try:
        img = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(img, lang="eng")

        return (
            "🖼 **تحليل الصورة**\n\n"
            f"النص المستخرج:\n{text}"
        )
    except:
        return "⚠ لا يمكن تحليل الصورة."

# -------------------------------
# استقبال الرسائل
# -------------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    # لو رسالة نصية → تحليل رابط
    if msg.text and msg.text.startswith("http"):
        result = analyze_link(msg.text)
        await msg.reply_text(result)
        return

    # لو صورة → تحليل OCR
    if msg.photo:
        file = await msg.photo[-1].get_file()
        file_bytes = await file.download_as_bytearray()
        result = analyze_image(file_bytes)
        await msg.reply_text(result)
        return

    await msg.reply_text("أرسل رابط أو صورة فقط.")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL, handle_message))
app.run_polling()
