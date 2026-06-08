import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import requests
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import io
import re

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحبًا بك في Dubai Property AI 👋\n\n"
        "أرسل رابط عقار أو صورة وسأقوم بتحليلها."
    )

def extract_unit_number_from_url(url: str):
    match = re.search(r"(\d{4,9})", url)
    return match.group(1) if match else None

def analyze_link(url: str):
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.find("h1")
        price = soup.find("span", string=lambda x: x and "AED" in x)
        area = soup.find("span", string=lambda x: x and ("sqft" in x.lower() or "sqm" in x.lower()))

        return (
            f"🏡 العنوان: {title.get_text(strip=True) if title else 'غير متوفر'}\n"
            f"💰 السعر: {price.get_text(strip=True) if price else 'غير متوفر'}\n"
            f"📐 المساحة: {area.get_text(strip=True) if area else 'غير متوفر'}\n"
        )
    except:
        return "⚠ لم أستطع تحليل الرابط."

def analyze_image(file_bytes: bytes):
    try:
        img = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(img, lang="eng")
        numbers = re.findall(r"\b\d{3,9}\b", text)

        result = "🖼 *تحليل الصورة*\n\n"
        result += f"📄 النص:\n{text}\n\n" if text.strip() else "لا يوجد نص واضح.\n\n"
        result += "🔢 أرقام محتملة:\n" + "\n".join(numbers) if numbers else "لا توجد أرقام واضحة."
        return result
    except:
        return "⚠ لم أستطع تحليل الصورة."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    if msg.text and ("http://" in msg.text or "https://" in msg.text):
        await msg.reply_text("⏳ جاري التحليل...")
        reply = analyze_link(msg.text)
        unit = extract_unit_number_from_url(msg.text)
        if unit:
            reply += f"\n🔢 رقم العقار: {unit}"
        await msg.reply_text(reply)
        return

    if msg.photo:
        await msg.reply_text("⏳ جاري تحليل الصورة...")
        file = await msg.photo[-1].get_file()
        file_bytes = await file.download_as_bytearray()
        result = analyze_image(file_bytes)
        await msg.reply_text(result, parse_mode="Markdown")
        return

    await msg.reply_text("أرسل رابط عقار أو صورة.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
