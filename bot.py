from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import time
from datetime import date

TOKEN = "8937129811:AAHmwlXc5iCPOU8K8v3GfeRqbgstQPC5ap4"

# -------------------------------
# Temporary storage (Version 0.2)
# -------------------------------
study_sessions = {}   # user_id -> start timestamp
daily_totals = {}     # user_id -> {"date": "YYYY-MM-DD", "seconds": total}


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


# -------------------------------
# Commands
# -------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to StudyNest!\n\n"
        "Available commands:\n\n"
        "📚 /startstudy - Start studying\n"
        "🛑 /stopstudy - Stop studying\n"
        "📅 /today - Today's study time"
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


# -------------------------------
# Bot
# -------------------------------
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("startstudy", startstudy))
app.add_handler(CommandHandler("stopstudy", stopstudy))
app.add_handler(CommandHandler("today", today))

print("🤖 StudyNest v0.2 running...")

app.run_polling()