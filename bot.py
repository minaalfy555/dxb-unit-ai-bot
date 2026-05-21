    if not url.startswith("http"):
        await update.message.reply_text("من فضلك أرسل رابط إعلان صحيح.")
        return

    # محاولة استخراج رقم من اللينك
    match = re.search(r'(\d+)', url)

    if match:
        unit_number = match.group(1)
        await update.message.reply_text(f"🔢 رقم العقار المستخرج من الرابط:\n{unit_number}")
    else:
        await update.message.reply_text("❗ الرابط لا يحتوي على رقم عقار.")
python3.11 bot.py

