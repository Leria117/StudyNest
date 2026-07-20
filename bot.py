from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import time
from datetime import date

TOKEN = "8937129811:AAHmwlXc5iCPOU8K8v3GfeRqbgstQPC5ap4"

# -------------------------------
# Temporary storage (Version 0.4 Beta)
# -------------------------------

study_sessions = {}      # user_id -> start timestamp
daily_totals = {}        # user_id -> {"date": ..., "seconds": ...}

waiting_users = []       # Users waiting for a partner
partners = {}            # user_id -> partner_id

# -------------------------------
# Helper
# -------------------------------
def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours}h {minutes}m {secs}s"


def get_today_record(user_id):
    """Returns today's record, resetting it automatically if the date changed."""
    today = str(date.today())

    if user_id not in daily_totals:
        daily_totals[user_id] = {
            "date": today,
            "seconds": 0
        }

    elif daily_totals[user_id]["date"] != today:
        daily_totals[user_id] = {
            "date": today,
            "seconds": 0
        }

    return daily_totals[user_id]

def get_keyboard():
    keyboard = [
        ["📚 Start Studying", "🛑 Stop Studying"],
        ["📅 Today", "🤝 Study Buddy"],
        ["🗑 Reset"]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )
# -------------------------------
# Commands
# -------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to StudyNest!\n\n"
        "Choose an option below! 👇",
        reply_markup=get_keyboard()
    )
        
async def startstudy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Make sure today's record exists
    get_today_record(user_id)

    if user_id in study_sessions:
        await update.message.reply_text(
            "📚 You're already studying!"
        )
        return

    study_sessions[user_id] = time.time()

    await update.message.reply_text(
        "✅ Study session started!\n\n"
        "Good luck! 🍀"
    )

    # Notify partner if they have one
    if user_id in partners:
        partner_id = partners[user_id]

        try:
            await context.bot.send_message(
                chat_id=partner_id,
                text="🟢 Your study buddy has started studying!\n\nGood luck to both of you! 📚"
            )
        except:
            pass


async def stopstudy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in study_sessions:
        await update.message.reply_text(
            "❌ You haven't started studying.\nUse /startstudy first."
        )
        return

    record = get_today_record(user_id)

    elapsed = int(time.time() - study_sessions.pop(user_id))

    record["seconds"] += elapsed

    await update.message.reply_text(
        f"✅ Study session finished!\n\n"
        f"⏱ Session: {format_time(elapsed)}\n"
        f"📅 Today: {format_time(record['seconds'])}"
    )

    # Notify partner
    if user_id in partners:
        partner_id = partners[user_id]

        try:
            await context.bot.send_message(
                chat_id=partner_id,
                text=(
                    "📚 Your study buddy finished a study session!\n\n"
                    f"⏱ Session: {format_time(elapsed)}\n"
                    f"📅 Today's total: {format_time(record['seconds'])}"
                )
            )
        except:
            pass

  
async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    record = get_today_record(user_id)

    total = record["seconds"]

    message = ""

    if user_id in study_sessions:
        current_session = int(time.time() - study_sessions[user_id])
        total += current_session

        message += (
            "📚 You are currently studying.\n\n"
            f"Current session: {format_time(current_session)}\n\n"
        )

    message += f"📅 Today's total:\n{format_time(total)}"

    await update.message.reply_text(message)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    record = get_today_record(user_id)
    record["seconds"] = 0

    if user_id in study_sessions:
        study_sessions.pop(user_id)

    await update.message.reply_text(
        "🗑 Today's study time has been reset.\n\n"
        "📅 Today: 0h 0m 0s"
    )

async def studybuddy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Already has a partner
    if user_id in partners:
        await update.message.reply_text(
            "🤝 You already have a study buddy!\n\n"
            "Use /skip if you want a different partner."
        )
        return

    # Already waiting
    if user_id in waiting_users:
        await update.message.reply_text(
            "🔍 You're already waiting for a study buddy..."
        )
        return

    # Someone is waiting
    if waiting_users:
        partner_id = waiting_users.pop(0)

        partners[user_id] = partner_id
        partners[partner_id] = user_id

        await update.message.reply_text(
            "🎉 Study buddy found!\n\n"
            "Good luck studying together! 📚"
        )

        await context.bot.send_message(
            chat_id=partner_id,
            text="🎉 Study buddy found!\n\nGood luck studying together! 📚"
        )

    else:
        waiting_users.append(user_id)

        await update.message.reply_text(
            "🔍 Looking for a study buddy...\n\n"
            "You'll be notified when someone joins!"
        )
# -------------------------------
# Bot
# -------------------------------
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("startstudy", startstudy))
app.add_handler(CommandHandler("stopstudy", stopstudy))
app.add_handler(CommandHandler("today", today))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(CommandHandler("studybuddy", studybuddy))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📚 Start Studying":
        await startstudy(update, context)

    elif text == "🛑 Stop Studying":
        await stopstudy(update, context)

    elif text == "📅 Today":
        await today(update, context)

    elif text == "🤝 Study Buddy":
        await studybuddy(update, context)

    elif text == "🗑 Reset":
        await reset(update, context)
# -------------------------------
# Bot
# -------------------------------

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("startstudy", startstudy))
app.add_handler(CommandHandler("stopstudy", stopstudy))
app.add_handler(CommandHandler("today", today))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(CommandHandler("studybuddy", studybuddy))

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler)
)

print("🤖 StudyNest v0.4 Beta running...")

app.run_polling()