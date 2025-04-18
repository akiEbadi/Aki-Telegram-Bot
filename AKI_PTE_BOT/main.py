BOT_TOKEN = "7803010061:AAFM4OauyJvmNtyXeAyiXQmkjBck1sICDhM"

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
import jdatetime

# ذخیره تسک‌ها و وضعیت هر کاربر
user_tasks = {}
user_descriptions = {}

# توضیحات هر تسک
TASK_DESCRIPTIONS = {
    "Reading": "انجام و تحلیل حداقل 5 متن RWFIB یا RFIB",
    "WE": "انجام 5 تسک WE",
    "SST": "انجام 1 یا 2 تسک Summarize Spoken Text",
    "SWT": "انجام 1 یا 2 تسک Summarize Written Text",
    "DI": " انجام حداقل 1 تسک یا 30 دقیقه تمرین Describe Image",
    "RL": "انجام حداقل 1 تسک یا 30 دقیقه تمرین Retell Lecture",
    "WFD": "یک ساعت تایپ و بررسی یا یک مرتبه گوش دادن به کل preiction",
    "RO": "انجام 2 تا 3 تمرین Read Aloud",
    "RA": "انجام 30 دقیقه تمرین Read Aloud",
    "RS": "انجام 30 دقیقه تمرین Repeat Sentence",
    "LFIB": "تست زدن یا تمرین PDF به مدت نیم ساعت",
    "HIW": "انجام 15 دقیقه تمرین Highlight Incorrect Words",
    "ASQ": "انجام 15 دقیقه تمرین Answer Short Question",
    "Mock": "یک بار آزمون کامل و بررسی به مدت 3 ساعت"
}

help_text = (
    "📋 راهنمای دستورات:\n\n"
    "/start - نمایش چک‌لیست امروز.\n"
    "/reset - ریست کردن چک‌لیست برای روز جدید.\n"
    "/share - ارسال چک‌لیست به صورت پیام متنی برای اشتراک‌گذاری.\n"
    "/help - نمایش این راهنما.\n"
    "/add [عنوان تسک] - افزودن تسک جدید.\n"
    "/remove [عنوان تسک] - حذف یک تسک از چک‌لیست."
)

# گرفتن تاریخ شمسی
def get_today_date():
    j_date = jdatetime.date.today()
    return j_date.year, j_date.month, j_date.day

# ساخت کیبورد چک‌لیست
def build_keyboard(user_id):
    tasks = user_tasks.get(user_id, {})
    keyboard = []
    for task, done in tasks.items():
        text = f"{'✅' if done else '⬜️'} {task}"
        keyboard.append([InlineKeyboardButton(text, callback_data=task)])
    return InlineKeyboardMarkup(keyboard)

# هدر چک‌لیست
def build_header(user_id):
    year, month, day = get_today_date()
    return f"📅 تاریخ: {year}/{month}/{day}\n📚 امروز چقدر خوندی؟\nکامل ✅  اصلا نخوندم ⬜️\n\n📋 *لیست تسک‌ها:*"

# راهنمای داخلی پیام
def build_guide():
    return (
        "\n\n📚 *راهنمای بات:* \n\n"
        "نمایش چک‌لیست امروز میتونی از دستور:\n"
        "/start \n\n"
        "ریست کردن چک‌لیست:\n"
        "/reset \n\n"
        "برای اشتراک‌گذاری یا گرفتن خروجی از چک‌لیست امروز:\n"
        "/share: \n\n"
        "افزودن تسک جدید:\n"
        "/add \[نام تسک جدید] \[(توضیحات)] \n\n"
        "حذف تسک: \n"
        "/remove [نام تسک موجود] \n\n"
        "مشاهده راهنمای کامل:\n"
        "/help"
    )

# نمایش لیست تسک‌ها با راهنما
async def show_checklist(update, context):
    user_id = update.effective_user.id
    await update.message.reply_text(
        build_header(user_id),
        reply_markup=build_keyboard(user_id),
        parse_mode='Markdown'
    )
    await update.message.reply_text(build_guide(), parse_mode='Markdown')


# ساخت پیام متنی چک‌لیست
def build_checklist_message(user_id):
    year, month, day = get_today_date()
    message = f"📅 تاریخ: {year}/{month}/{day}\n\n📋 چک لیست:\n"
    tasks = user_tasks.get(user_id, {})
    for task, done in tasks.items():
        status = "✅" if done else "⬜️"
        desc = TASK_DESCRIPTIONS.get(task, "بدون توضیح.")
        message += f"{status} {task} ({desc})\n"
    return message

# ارسال چک‌لیست به صورت پیام متنی
async def share(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_tasks:
        user_tasks[user_id] = {task: False for task in TASK_DESCRIPTIONS}
    checklist_message = build_checklist_message(user_id)
    await update.message.reply_text(checklist_message, parse_mode='Markdown')
    await update.message.reply_text(help_text)

# دستور راهنما
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(help_text)

# شروع بات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_tasks:
        user_tasks[user_id] = {task: False for task in TASK_DESCRIPTIONS}
    welcome_message = (
        "سلام! به بات مطالعه PTE خوش اومدی 🌱\n"
        "تسک‌های امروزت رو تیک بزن و پیشرفتت رو ثبت کن. \n"
        "میتونی تسک های دلخواهت رو اضافه یا حذف کنی \n"
        "میتونی لیست تسک هایی که امروز مطاله کردی به اشتراک بذاری \n"
        "میتونی برای فرداچک لیستت رو ریست کنی ولی یادت نره قبلش از چک لیست امروز یه خروجی بگیری"
    )
    await update.message.reply_text(welcome_message)
    await update.message.reply_text(
        build_header(user_id) + build_guide(),
        reply_markup=build_keyboard(user_id),
        parse_mode='Markdown'
    )

# دکمه کلیک شده
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    task = query.data
    if user_id in user_tasks and task in user_tasks[user_id]:
        user_tasks[user_id][task] = not user_tasks[user_id][task]
    await query.edit_message_text(
        build_header(user_id) + build_guide(),
        reply_markup=build_keyboard(user_id),
        parse_mode='Markdown'
    )
    desc = TASK_DESCRIPTIONS.get(task, "توضیحی موجود نیست.")
    await query.answer(desc)

# ریست چک‌لیست
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_tasks:
        for task in user_tasks[user_id]:
            user_tasks[user_id][task] = False
        year, month, day = get_today_date()
        await update.message.reply_text(f"♻️ چک‌لیست برای تاریخ {year}/{month}/{day} ریست شد.\nبرای شروع دوباره /start بزن.")

# افزودن تسک جدید
async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if len(context.args) == 0:
        await update.message.reply_text("لطفاً نام تسک را وارد کنید. مثال:\n /add RMCS")
        return
    task_name = " ".join(context.args)
    user_tasks.setdefault(user_id, {})[task_name] = False
    await update.message.reply_text(f"✅ تسک جدید \"{task_name}\" اضافه شد.")
    # TODO: show help

# حذف تسک
async def remove_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if len(context.args) == 0:
        await update.message.reply_text("لطفاً نام تسکی که می‌خواهید حذف شود را وارد کنید. مثال: /remove Listening")
        return
    task_name = " ".join(context.args)
    if user_id in user_tasks and task_name in user_tasks[user_id]:
        del user_tasks[user_id][task_name]
        await update.message.reply_text(f"❌ تسک \"{task_name}\" حذف شد.")
    else:
        await update.message.reply_text("❗️ تسک پیدا نشد.")

# اجرای بات
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(CommandHandler("share", share))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("add", add_task))
app.add_handler(CommandHandler("remove", remove_task))
app.add_handler(CallbackQueryHandler(button_handler))

print("🤖 Bot is running...")
app.run_polling()
