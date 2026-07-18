from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import time

TOKEN = "8937129811:AAHmwlXc5iCPOU8K8v3GfeRqbgstQPC5ap4"

# ---------- Temporary storage (Version 0.1) ----------
study_sessions = {}
daily_totals = {}

# ---------- Commands ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to StudyNest!\n\n"
        "Commands:\n"
        "/startstudy - Start studying\n"
        "/stopstudy - Stop studying\n"
        "/today - Show today's study time"
    )

async def startstudy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in study_sessions:
        await update.message.reply_text("📚 You're already studying!")
        return

    study_sessions[user_id] = time.time()

    await update.message.reply_text(
        "📚 Study session started!\n\n"
        "Good luck! 🍀"
    )

async def stopstudy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in study_sessions:
        await update.message.reply_text(
            "❌ You haven't started a study session.\nUse /startstudy first."
        )
        return

    start_time = study_sessions.pop(user_id)
    seconds = int(time.time() - start_time)

    daily_totals[user_id] = daily_totals.get(user_id, 0) + seconds

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    total = daily_totals[user_id]
    total_hours = total // 3600
    total_minutes = (total % 3600) // 60

    await update.message.reply_text(
        f"✅ Study session finished!\n\n"
        f"⏱️ Session: {hours}h {minutes}m\n"
        f"📅 Today: {total_hours}h {total_minutes}m"
    )

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    total = daily_totals.get(user_id, 0)

    hours = total // 3600
    minutes = (total % 3600) // 60

    await update.message.reply_text(
        f"📅 Today's study time:\n\n"
        f"{hours}h {minutes}m"
    )

# ---------- Build Bot ----------
app = (
    Application.builder()
    .token(TOKEN)
    .build()
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("startstudy", startstudy))
app.add_handler(CommandHandler("stopstudy", stopstudy))
app.add_handler(CommandHandler("today", today))

print("🤖 StudyNest Version 0.1 is running...")

app.run_polling()