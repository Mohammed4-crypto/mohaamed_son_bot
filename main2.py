import asyncio
import logging
import os
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
OWNER_ID = os.environ.get("OWNER_ID", "").strip()

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

MAX_TELEGRAM_LEN = 4000


def _ask_gemini_sync(question: str) -> str:
    if not client:
        return "مفتاح GEMINI_API_KEY غير مضبوط حالياً."
    prompt = (
        "أنت مساعد تعليمي متخصص في المنهج السوداني. أجب بوضوح وبساطة ودقة "
        "وبلغة عربية واضحة ومناسبة للطالب:\n\n"
        f"{question}"
    )
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )
    return (response.text or "").strip() or "لم أتمكن من توليد إجابة حالياً."


async def send_long_message(update: Update, text: str) -> None:
    if not update.message:
        return
    for i in range(0, len(text), MAX_TELEGRAM_LEN):
        part = text[i : i + MAX_TELEGRAM_LEN]
        await update.message.reply_text(part)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    await update.message.reply_text(
        "أهلاً بك في بوت محمد للمنهج السوداني.\n"
        "أرسل سؤالك أو درسك الآن وسأساعدك في شرحه وتبسيطه."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    user_text = update.message.text.strip()
    if not user_text:
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        answer = await asyncio.to_thread(_ask_gemini_sync, user_text)
    except Exception as exc:
        logger.exception("Error while generating Gemini response: %s", exc)
        answer = "حدث خطأ أثناء الاتصال بالمساعد الذكي، يرجى المحاولة مرة أخرى بعد قليل."

    await send_long_message(update, answer)


def main() -> None:
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN is missing in environment variables.")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting Mohammed bot...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
