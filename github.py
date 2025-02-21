import telebot
import logging
import time
import re
import threading
import os
from telebot import util
from datetime import datetime

# 🔑 Bot Credentials
TOKEN = "7856273648:AAHTl1o2YfFeVR01hvIABOZqfwQjWIRkLDM"  # ⛔ Change this later for security
DEST_CHANNELS = ["-1002489901746", "-1002461202593"]  # Multiple Channel IDs
ADMIN_IDS = ["7040674797", "6433288857"]  # ✅ Multiple Admin User IDs

if not TOKEN:
    raise ValueError("❌ Bot Token is missing! Please set a valid Token.")

# 📌 Logging Setup
logging.basicConfig(filename="bot.log", level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger()

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")  # ✅ Use HTML Parse Mode

# 🚫 Unwanted patterns to clean captions
UNWANTED_PATTERNS = [
    r"Tg[-:\s]*",
    r"@\w+",  # Removes any @username except @FilmyEmpire
    r"www.", r"http://", r"https://",  # Removes links
    r"[{}]",  # Removes brackets
    r"\s{2,}"  # Removes extra spaces
]

# 📋 Set Bot Commands (for menu button)
def set_bot_commands():
    commands = [
        telebot.types.BotCommand("start", "Start the bot"),
        telebot.types.BotCommand("stop", "Stop the bot")
    ]
    bot.set_my_commands(commands)

# 🚦 Bot Running Flag
is_bot_running = False

# 📝 Function to format caption with bold and clickable link
def format_caption(file_name):
    cleaned_name = file_name.strip()

    for pattern in UNWANTED_PATTERNS:
        cleaned_name = re.sub(pattern, "", cleaned_name, flags=re.IGNORECASE).strip()

    cleaned_name = re.sub(r'[^a-zA-Z0-9 @._-]', '', cleaned_name)

    # ✅ HTML Parse Mode for Bold + Clickable Title
    caption = f"<b><a href='https://t.me/FilmyEmpire'>{cleaned_name}</a></b>\n\n<b>⚡️ Join ➥</b> ⟦@FilmyEmpire⟧"

    logger.info(f"📋 Formatted Caption: {caption}")
    return caption

# 📥 Handle Media Files
@bot.message_handler(content_types=["document", "video", "photo"])
def handle_media(message):
    global is_bot_running

    if not is_bot_running:
        bot.send_message(message.chat.id, "⚠️ Bot is currently stopped. Use /start to activate.")
        return

    file_id, file_name, file_type = None, None, None

    if message.document:
        file_id, file_name, file_type = message.document.file_id, message.document.file_name, "document"
    elif message.video:
        file_id, file_name, file_type = message.video.file_id, message.video.file_name, "video"
    elif message.photo:
        file_id, file_name, file_type = message.photo[-1].file_id, "Photo", "photo"

    if not file_id or not file_name:
        logger.warning("⚠️ File information missing!")
        return

    caption = format_caption(file_name)

    try:
        for channel in DEST_CHANNELS:
            if file_type == "document":
                util.antiflood(bot.send_document, channel, file_id, caption=caption, parse_mode="HTML")
            elif file_type == "video":
                util.antiflood(bot.send_video, channel, file_id, caption=caption, parse_mode="HTML")
            elif file_type == "photo":
                util.antiflood(bot.send_photo, channel, file_id, caption=caption, parse_mode="HTML")

        logger.info(f"✅ File sent: {file_name}")
        print(f"✅ File sent: {file_name}")

    except Exception as e:
        logger.error(f"❌ Error sending {file_name}: {e}")
        print(f"❌ Error sending {file_name}: {e}")

# 🚀 Start Command
@bot.message_handler(commands=["start"])
def start_bot(message):
    global is_bot_running
    if str(message.from_user.id) in ADMIN_IDS:
        is_bot_running = True
        bot.send_message(message.chat.id, "✅ Bot started and running.")
        logger.info(f"🚀 Bot started by admin: {message.from_user.id}")
    else:
        bot.send_message(message.chat.id, "❌ You are not authorized to start the bot.")

# 🛑 Stop Command
@bot.message_handler(commands=["stop"])
def stop_bot(message):
    global is_bot_running
    if str(message.from_user.id) in ADMIN_IDS:
        is_bot_running = False
        bot.send_message(message.chat.id, "🛑 Bot has been stopped.")
        logger.info(f"🛑 Bot stopped by admin: {message.from_user.id}")
    else:
        bot.send_message(message.chat.id, "❌ You are not authorized to stop the bot.")

# 🔄 Bot Polling
def start_polling():
    set_bot_commands()
    print("🤖 Bot is running...")
    bot.polling(none_stop=True)

# 🚀 Main
if __name__ == "__main__":
    start_polling()