# from dotenv import load_dotenv
import os

try:
    import dotenv
    print("python-dotenv is installed!") 
except ImportError:
    print("python-dotenv is NOT installed!")
    BOT_TOKEN = "7803010061:AAH_X9RM_EMHX8g4se6lAGbVQCIvt8RCT70"
    
dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
print("BOT_TOKEN:", BOT_TOKEN)

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
import jdatetime

user_tasks = {}
user_descriptions = {}

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

def get_today_date():
    j_date = jdatetime.date.today()
    return j_date.year, j_date.month, j_date.day

def build_keyboard(user_id):
    tasks = user_tasks.get(user_id, {})
    keyboard = []
    for task, done in tasks.items():
        text = f"{'✅' if done else '⬜️'} {task}"
        keyboard.append([InlineKeyboardButton(text, callback_data=task)])
    return InlineKeyboardMarkup(keyboard)

def build_header(user_id):
    year, month, day = get_today_date()
    return f"📅 تاریخ: {year}/{month}/{day}\n📚 امروز چقدر خوندی؟\nکامل ✅  اصلا نخوندم ⬜️\n\n📋 *لیست تسک‌ها:*"

def build_guide():
    return (
        "\n\n📚 *راهنمای بات:* \n\n"
        "نمایش چک‌لیست امروز میتونی از دستور:\n"
        "/start \n\n"
        "ریست کردن چک‌لیست:\n"
        "/reset \n\n"
        "گرفتن خروجی از چک‌لیست امروز بدون توضیحات:\n"
        "/print: \n\n"
        "گرفتن خروجی از چک‌لیست امروز با توضیحات:\n"
        "/show: \n\n"
        "افزودن تسک جدید:\n"
        "/add نام تسک جدید : توضیحات   \n\n"
        "/add Task Name : Description   \n\n"
        "حذف تسک: \n"
        "/remove نام تسک موجود \n\n"
        "مشاهده راهنمای کامل:\n"
        "/help"
    )

async def show_checklist(update, context):
    user_id = update.effective_user.id
    await update.message.reply_text(
        build_header(user_id),
        reply_markup=build_keyboard(user_id),
        parse_mode='Markdown'
    )
    await update.message.reply_text(build_guide(), parse_mode='Markdown')

def build_checklist_message(user_id, with_description=False):
    year, month, day = get_today_date()
    message = f"📅 تاریخ: {year}/{month}/{day}\n\n📋 چک لیست:\n"
    tasks = user_tasks.get(user_id, {})
    for task, done in tasks.items():
        status = "✅" if done else "⬜️"
        if with_description:
            desc = user_descriptions.get(user_id, {}).get(task) or TASK_DESCRIPTIONS.get(task, "بدون توضیح.")
            message += f"{status} {task} ({desc})\n"
        else:
            message += f"{status} {task}\n"
    return message

async def print_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_tasks:
        user_tasks[user_id] = {task: False for task in TASK_DESCRIPTIONS}
    checklist_message = build_checklist_message(user_id, with_description=False)
    await update.message.reply_text(checklist_message, parse_mode='Markdown')

async def show_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_tasks:
        user_tasks[user_id] = {task: False for task in TASK_DESCRIPTIONS}
    checklist_message = build_checklist_message(user_id, with_description=True)
    await update.message.reply_text(checklist_message, parse_mode='Markdown')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(build_guide(), parse_mode='Markdown')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_tasks:
        user_tasks[user_id] = {task: False for task in TASK_DESCRIPTIONS}
    welcome_message = (
        "سلام! به بات مطالعه PTE خوش اومدی 🌱\n"
        "تسک‌های امروزت رو تیک بزن و پیشرفتت رو ثبت کن. \n"
        "میتونی تسک های دلخواهت رو اضافه یا حذف کنی \n"
        "میتونی لیست تسک هایی که امروز مطالعه کردی به اشتراک بذاری \n"
        "میتونی برای فردا چک لیستت رو ریست کنی ولی یادت نره قبلش از چک لیست امروز یه خروجی بگیری"
    )
    await update.message.reply_text(welcome_message)
    await update.message.reply_text(
        build_header(user_id) + build_guide(),
        reply_markup=build_keyboard(user_id),
        parse_mode='Markdown'
    )

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
    desc = user_descriptions.get(user_id, {}).get(task) or TASK_DESCRIPTIONS.get(task, "توضیحی موجود نیست.")
    await query.answer(desc)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_tasks:
        for task in user_tasks[user_id]:
            user_tasks[user_id][task] = False
        year, month, day = get_today_date()
        await update.message.reply_text(f"♻️ چک‌لیست برای تاریخ {year}/{month}/{day} ریست شد.\nبرای شروع دوباره /start بزن.")

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if len(context.args) == 0:
        await update.message.reply_text("لطفاً نام تسک را وارد کنید. مثال:\n" 
                                        "/add نام تسک جدید : توضیحات\n"
                                        "/add Task Name : Description\n\n"
                                        "/help : راهنمای دستورات")
        return

    text = " ".join(context.args)
    if ":" in text:
        task_name, description = map(str.strip, text.split(":", 1))
    else:
        task_name, description = text.strip(), ""

    user_tasks.setdefault(user_id, {})[task_name] = False

    if description:
        user_descriptions.setdefault(user_id, {})[task_name] = description
        await update.message.reply_text(f"✅ تسک جدید \"{task_name}\" با توضیح ذخیره شد.")
    else:
        await update.message.reply_text(f"✅ تسک جدید \"{task_name}\" بدون توضیح اضافه شد.")

async def remove_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if len(context.args) == 0:
        await update.message.reply_text("لطفاً نام تسکی که می‌خواهید حذف شود را وارد کنید. مثال:\n"
                                        "/remove ASQ \n\n"
                                        "/help : راهنمای دستورات")
        return

    task_name = " ".join(context.args)
    existed = False

    if user_id in user_tasks and task_name in user_tasks[user_id]:
        del user_tasks[user_id][task_name]
        existed = True

    if user_id in user_descriptions and task_name in user_descriptions[user_id]:
        del user_descriptions[user_id][task_name]

    if existed:
        await update.message.reply_text(f"❌ تسک \"{task_name}\" حذف شد.")
    else:
        await update.message.reply_text("❗️ تسک پیدا نشد.")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(CommandHandler("print", print_list))
app.add_handler(CommandHandler("show", show_description))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("add", add_task))
app.add_handler(CommandHandler("remove", remove_task))
app.add_handler(CallbackQueryHandler(button_handler))

print("🤖 Bot is running...")
app.run_polling()
