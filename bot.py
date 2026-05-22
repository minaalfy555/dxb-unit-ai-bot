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

# حط توكن البوت هنا
TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"


# ---------------------------
# /start
# ---------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحبًا بك في Dubai Property AI 👋\n\n"
        "أنا أقدر أعمل لك:\n"
        "1️⃣ تحليل روابط العقارات (Bayut / Property Finder / Dubizzle / Developers)\n"
        "   • أستخرج العنوان – السعر – المساحة (إن وُجدت)\n"
        "   • أستخرج رقم العقار من الرابط.\n\n"
        "2️⃣ تحليل الصور (Screenshots / Floor plans / Maps)\n"
        "   • أقرأ النص داخل الصورة (OCR)\n"
        "   • أحاول أستخرج أرقام الوحدات من الصورة.\n\n"
        "أرسل الآن:\n"
        "• رابط إعلان عقار\n"
        "أو\n"
        "• صورة متعلقة بالعقار."
    )


# ---------------------------
# استخراج رقم اليونت من الرابط
# ---------------------------
def extract_unit_number_from_url(url: str) -> str | None:
    """
    نحاول نلقط أي رقم مكوّن من 4–9 أرقام من الرابط.
    مثال:
    https://www.bayut.com/property/details-1234567.html  → 1234567
    """
    match = re.search(r"(\d{4,9})", url)
    if match:
        return match.group(1)
    return None


# ---------------------------
# تحليل صفحة الإعلان (عنوان / سعر / مساحة)
# ---------------------------
def analyze_link(url: str) -> str:
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return "⚠ الرابط لا يفتح أو الموقع لا يستجيب."

        soup = BeautifulSoup(r.text, "html.parser")

        # محاولات عامة لاستخراج بيانات
        title = soup.find("h1")
        price = soup.find(
            "span",
            string=lambda x: x
            and isinstance(x, str)
            and any(p in x for p in ["AED", "درهم", "د.إ"]),
        )
        area = soup.find(
            "span",
            string=lambda x: x
            and isinstance(x, str)
            and any(w in x.lower() for w in ["sqft", "sqm", "m²"]),
        )

        title_text = title.get_text(strip=True) if title else "غير متوفر"
        price_text = price.get_text(strip=True) if price else "غير متوفر"
        area_text = area.get_text(strip=True) if area else "غير متوفر"

        return (
            "🏡 *تحليل إعلان العقار*\n\n"
            f"• العنوان: {title_text}\n"
            f"• السعر: {price_text}\n"
            f"• المساحة: {area_text}\n"
        )
    except Exception:
        return "⚠ لم أستطع تحليل هذا الرابط. جرّب رابط آخر أو تأكد أن الموقع يعمل."


# ---------------------------
# تحليل الصورة (OCR + أرقام)
# ---------------------------
def analyze_image(file_bytes: bytes) -> str:
    try:
        img = Image.open(io.BytesIO(file_bytes))

        # قراءة النص من الصورة
        text = pytesseract.image_to_string(img, lang="eng")

        # نحاول نلقط أرقام تشبه أرقام الوحدات
        numbers = re.findall(r"\b\d{3,9}\b", text)
        numbers = list(dict.fromkeys(numbers))  # إزالة التكرار

        result = "🖼 *تحليل الصورة*\n\n"
        if text.strip():
            result += f"📄 النص المستخرج من الصورة:\n{text.strip()}\n\n"
        else:
            result += "لم أستطع قراءة نص واضح من الصورة.\n\n"

        if numbers:
            result += "🔢 أرقام محتملة للوحدات أو العقارات داخل الصورة:\n"
            result += "\n".join(f"- {n}" for n in numbers)
        else:
            result += "لم أجد أرقام وحدات واضحة في الصورة."

        return result
    except Exception:
        return "⚠ لم أستطع تحليل هذه الصورة. جرّب صورة أوضح أو مختلفة."


# ---------------------------
# استقبال أي رسالة
# ---------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    # 1) لو رسالة نصية فيها رابط
    if msg.text and ("http://" in msg.text or "https://" in msg.text):
        url = msg.text.strip()
        await msg.reply_text("⏳ جاري تحليل رابط العقار واستخراج رقم الوحدة...")

        # تحليل الإعلان
        analysis = analyze_link(url)

        # استخراج رقم اليونت من الرابط
        unit_from_url = extract_unit_number_from_url(url)
        if unit_from_url:
            unit_part = (
                f"🔢 *رقم العقار المستخرج من الرابط:*\n{unit_from_url}\n"
            )
        else:
            unit_part = "❗ لم أستطع العثور على رقم عقار واضح في الرابط.\n"

        reply = analysis + "\n" + unit_part
        await msg.reply_text(reply, parse_mode="Markdown")
        return

    # 2) لو صورة → تحليل OCR + أرقام
    if msg.photo:
        await msg.reply_text("⏳ جاري تحليل الصورة واستخراج النص والأرقام المحتملة...")
        file = await msg.photo[-1].get_file()
        file_bytes = await file.download_as_bytearray()
        result = analyze_image(file_bytes)
        await msg.reply_text(result, parse_mode="Markdown")
        return

    # 3) أي شيء آخر
    await msg.reply_text(
        "أرسل رابط إعلان عقار لتحليله، أو صورة متعلقة بالعقار لتحليلها."
    )


# ---------------------------
# تشغيل البوت
# ---------------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handle_message))

    app.run_polling()


if __name__ == "__main__":
    main()
