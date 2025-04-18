BOT_TOKEN = "7803010061:AAFM4OauyJvmNtyXeAyiXQmkjBck1sICDhM"

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
from datetime import datetime
import jdatetime

# اطلاعات چک‌لیست برای هر کاربر به صورت دیکشنری
user_tasks = {}

help_text = (
    "📋 راهنمای دستورات:\n\n"
    "/start: نمایش چک‌لیست برای امروز.\n"
    "/reset: ریست کردن چک‌لیست برای روز جدید.\n"
    "/share: ارسال چک‌لیست به صورت یک پیام متنی برای اشتراک‌گذاری.\n"
    "/help: نمایش این راهنما."
)
# گرفتن تاریخ شمسی
def get_today_date():
    today = datetime.now()
    j_date = jdatetime.date.today()  # تاریخ شمسی امروز
    return j_date.year, j_date.month, j_date.day

# ساخت کیبورد چک‌لیست
def build_keyboard(user_id):
    tasks = user_tasks.get(user_id, {})
    keyboard = []
    for task, done in tasks.items():
        text = f"{'✅' if done else '⬜️'} {task}"
        keyboard.append([InlineKeyboardButton(text, callback_data=task)])
    return InlineKeyboardMarkup(keyboard)

# پیام بالا (هدر چک‌لیست) با تاریخ شمسی
def build_header(user_id):
    year, month, day = get_today_date()
    return f"📅 تاریخ: {year}/{month}/{day}\n📚 امروز چقدر خوندی؟\nکامل ✅  اصلا نخوندم ⬜️\n\n📋 *لیست تسک‌ها:*"

# اضافه کردن راهنمای بات به چک‌لیست
def build_guide():
    return (
        "\n\n📚 *راهنمای بات:* \n\n"
        "/start: نمایش چک‌لیست امروز.\n"
        "برای ریست کردن چک‌لیست از دستور /reset استفاده کنید.\n"
        "برای اشتراک‌گذاری چک‌لیست از دستور /share استفاده کنید.\n"
        "برای مشاهده راهنمای کامل از دستور /help استفاده کنید."
    )

# ساخت چک‌لیست برای ارسال به صورت پیام متنی
def build_checklist_message(user_id):
    year, month, day = get_today_date()
    message = f"📅 تاریخ: {year}/{month}/{day}\n\n"
    message += "📋 چک لیست:\n"

    # اضافه کردن چک باکس‌ها و تسک‌ها به پیام
    tasks = user_tasks.get(user_id, {})
    for task, done in tasks.items():
        status = "✅" if done else "⬜️"
        message += f"{status} {task}\n"
    return message

# ارسال چک‌لیست به صورت یک پیام متنی
async def send_checklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_tasks:
        # اگر کاربر برای اولین بار است که از بات استفاده می‌کند، لیست تسک‌ها را ایجاد می‌کنیم
        user_tasks[user_id] = {
            "Reading (>= 5)": False,
            "WE (5)": False,
            "SST (1-2) with check": False,
            "SWT (1-2) with check": False,
            "DI (>= 1 or 30 min)": False,
            "RL (>= 1 or 30 min)": False,
            "WFD (1h type & check or 1 time listening to all)": False,
            "RO (2-3)": False,
            "RA (30 min)": False,
            "RS (30 min)": False,
            "LFIB (test or pdf)": False,
            "HIW (15 min)": False,
            "ASQ (15 min)": False
        }
    
    checklist_message = build_checklist_message(user_id)
    await update.message.reply_text(checklist_message, parse_mode='Markdown')
    await update.message.reply_text(help_text)
# راهنمای دستورات
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(help_text)

# /start command → ارسال چک‌لیست
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_tasks:
        # اگر کاربر برای اولین بار است که از بات استفاده می‌کند، لیست تسک‌ها را ایجاد می‌کنیم
        user_tasks[user_id] = {
            "Reading (>= 5)": False,
            "WE (5)": False,
            "SST (1-2) with check": False,
            "SWT (1-2) with check": False,
            "DI (>= 1 or 30 min)": False,
            "RL (>= 1 or 30 min)": False,
            "WFD (1h type & check or 1 time listening to all)": False,
            "RO (2-3)": False,
            "RA (30 min)": False,
            "RS (30 min)": False,
            "LFIB (test or pdf)": False,
            "HIW (15 min)": False,
            "ASQ (15 min)": False
        }

    # ارسال پیغام خوشامدگویی به همراه راهنمای دستورات
    welcome_message = (
        "سلام! به بات مطالعه PTE خوش آمدید.\n"
        "در اینجا شما می‌توانید چک‌لیست روزانه خود را پیگیری کنید و به راحتی آن را با دیگران به اشتراک بگذارید.\n"
    )
    await update.message.reply_text(welcome_message)

    # ارسال چک‌لیست و کیبورد بعد از پیام خوشامدگویی
    await update.message.reply_text(build_header(user_id), reply_markup=build_keyboard(user_id), parse_mode='Markdown')
    await update.message.reply_text(help_text)
# وقتی دکمه‌ها کلیک می‌شن
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    task = query.data
    user_tasks[user_id][task] = not user_tasks[user_id][task]
    await query.edit_message_text(build_header(user_id) + build_guide(), reply_markup=build_keyboard(user_id), parse_mode='Markdown')
    await query.answer()

# /reset command → ریست کامل چک‌لیست
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_tasks:
        for task in user_tasks[user_id]:
            user_tasks[user_id][task] = False
        year, month, day = get_today_date()
        await update.message.reply_text(f"♻️ چک‌لیست برای تاریخ {year}/{month}/{day} ریست شد.\nبرای شروع دوباره /start بزن.")

# راه‌اندازی بات
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(CommandHandler("share", send_checklist))  # ارسال چک‌لیست به صورت پیام متنی
app.add_handler(CommandHandler("help", help))  # اضافه کردن راهنمای دستورات
app.add_handler(CallbackQueryHandler(button_handler))

print("🤖 Bot is running...")
app.run_polling()
