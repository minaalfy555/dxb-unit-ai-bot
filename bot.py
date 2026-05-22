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
import re

# حط توكن البوت هنا
TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"


# ---------------------------
# /start
# ---------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحبًا بك في DXB Unit AI 👋\n\n"
        "✅ أرسل رابط إعلان عقار (Bayut / Property Finder / Dubizzle / Developer)\n"
        "وسأحاول:\n"
        "• تحليل الإعلان (عنوان / سعر / مساحة إن وُجدت)\n"
        "• استخراج رقم العقار من الرابط.\n\n"
        "📷 الصور: أرسل صورة الآن وسأخبرك أني استلمتها، "
        "وسنضيف تحليل الصور في المرحلة القادمة."
    )


# ---------------------------
# استخراج رقم اليونت من الرابط
# ---------------------------
def extract_unit_number(url: str) -> str | None:
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
            and any(p in x for p in ["AED", "درهم", "د.إ", "دبي"])
        )
        area = soup.find(
            "span",
            string=lambda x: x
            and isinstance(x, str)
            and any(w in x.lower() for w in ["sqft", "sqm", "m²"])
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
        unit = extract_unit_number(url)
        if unit:
            unit_part = f"🔢 *رقم العقار المستخرج من الرابط:*\n{unit}\n"
        else:
            unit_part = "❗ لم أستطع العثور على رقم عقار واضح في الرابط.\n"

        reply = analysis + "\n" + unit_part
        await msg.reply_text(reply, parse_mode="Markdown")
        return

    # 2) لو صورة (هنجهزها للتحليل لاحقًا)
    if msg.photo:
        await msg.reply_text(
            "📷 استلمت الصورة.\n"
            "في النسخة الجاية هضيف تحليل تلقائي لصور المخططات ولقطات الشاشة إن شاء الله."
        )
        return

    # 3) أي شيء آخر
    await msg.reply_text(
        "أرسل رابط إعلان عقار لتحليله، أو صورة (التحليل المتقدم للصور في المرحلة القادمة)."
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
