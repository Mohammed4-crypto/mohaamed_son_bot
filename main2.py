import os
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
OWNER_ID = os.environ.get("OWNER_ID", "").strip()

gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أهلاً بك في بوت محمد للمنهج السوداني. أرسل سؤالك أو درسك وسأساعدك بوضوح."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    if not gemini_client:
        await update.message.reply_text("مفتاح GEMINI_API_KEY غير مضبوط حالياً.")
        return

    prompt = (
        "أنت مساعد تعليمي متخصص في المنهج السوداني. أجب بوضوح وبساطة ودقة:\n\n"
        f"{update.message.text}"
    )
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    reply_text = response.text or "لم أتمكن من توليد إجابة حالياً."
    await update.message.reply_text(reply_text)


def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN is missing")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()
