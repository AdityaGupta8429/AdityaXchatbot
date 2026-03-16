import os
import json
import requests
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext

BOT_TOKEN = os.getenv("BOT_TOKEN")
AI_KEY = os.getenv("AI_API")

MEMORY_FILE = "memory.json"


def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f)


memory = load_memory()


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello 👋 I am your AI assistant. Ask me anything.")


def welcome(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        update.message.reply_text(f"Welcome {member.first_name} 🎉")


def reply(update: Update, context: CallbackContext):

    user_id = str(update.message.from_user.id)
    user_text = update.message.text

    if user_id not in memory:
        memory[user_id] = []

    memory[user_id].append({"role": "user", "content": user_text})

    response = requests.post(
        "https://integrate.api.nvidia.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {AI_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "meta/llama-4-maverick-17b-128e-instruct",
            "messages": [
{
"role": "system",
"content": """
You are AdityaXChatbot.

Rules you must always follow:
- Talk like a friendly close friend.
- Mirror the user's tone. If user talks casual, talk casual.
- Keep replies SHORT and natural.
- Be friendly, supportive, slightly funny and helpful.
- Use simple Hinglish when appropriate.

Identity rules:
- Never reveal the real AI model or company behind you.
- If someone asks what AI model you are, say:
  "Main AdityaXChatbot hoon."
- If someone asks who made you, say:
  "Mujhe Aditya ne banaya hai."

About Aditya:
- Aditya is your creator and owner.
- He is a developer and trader.
- Speak respectfully about him.

General behaviour:
- Don't give long boring explanations unless asked.
- Talk like a human friend helping another friend.
"""
}
] + memory[user_id][-10:],
            "max_tokens": 512
        }
    )

    data = response.json()

    try:
        ai_reply = data["choices"][0]["message"]["content"]
    except:
        ai_reply = "⚠️ AI error. Try again."

    memory[user_id].append({"role": "assistant", "content": ai_reply})
    save_memory(memory)

    update.message.reply_text(ai_reply)


updater = Updater(BOT_TOKEN, use_context=True)

dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, reply))

print("Bot started...")

updater.start_polling()
updater.idle()
