from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
 
from telegram.ext import CallbackQueryHandler

from dotenv import load_dotenv
import os
import logging
from datetime import datetime

load_dotenv()
TOKEN = os.environ["TG_BOT_TOKEN"]

logger = logging.getLogger(__name__)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),  # Запись в файл
        logging.StreamHandler()  # Вывод в консоль
    ]
)

logger = logging.getLogger(__name__)

# Логирование всех входящих обновлений
async def log_all_updates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        user = update.message.from_user
        logger.info(f"📨 Сообщение от {user.first_name} (@{user.username}, id:{user.id}): {update.message.text}")
    elif update.callback_query:
        user = update.callback_query.from_user
        logger.info(f"🔘 Нажатие кнопки от {user.first_name} (@{user.username}, id:{user.id}): {update.callback_query.data}")

# Состояния для ConversationHandler
NAME, AGE = range(2)

# Обычная клавиатура
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    user = update.message.from_user
    logger.info(f"✅ Пользователь {user.first_name} (@{user.username}) запустил бота")
    
    keyboard = [
        [KeyboardButton("Привет"), KeyboardButton("Пока")],
        [KeyboardButton("Анкета")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

# Inline клавиатура
async def inline_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Кнопка 1", callback_data="btn1")],
        [InlineKeyboardButton("Кнопка 2", callback_data="btn2")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажмите кнопку:", reply_markup=reply_markup)

# Обработка нажатий на inline кнопки
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "btn1":
        await query.edit_message_text("Нажата кнопка 1")
    elif query.data == "btn2":
        await query.edit_message_text("Нажата кнопка 2")

# Начало анкеты
async def survey_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Как вас зовут?")
    return NAME

async def survey_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Сколько вам лет?")
    return AGE

async def survey_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    age = update.message.text
    name = context.user_data["name"]
    await update.message.reply_text(f"Спасибо, {name}! Вам {age} лет.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Анкета отменена.")
    return ConversationHandler.END

# Обработка текстовых сообщений
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    if text == "привет":
        await update.message.reply_text("И тебе привет!")
    elif text == "пока":
        await update.message.reply_text("До свидания!")
    elif text == "анкета":
        await survey_start(update, context)
        return NAME
    else:
        await update.message.reply_text("Не понимаю :(")

#async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    
#    user = update.message.from_user
#    logger.info(f"✅ Пользователь {user.first_name} (@{user.username}) запустил бота")
    
    # Сохраняем информацию о пользователе
#    context.user_data['start_time'] = datetime.now()
#    context.user_data['user_id'] = user.id
    
#    keyboard = [
#        [InlineKeyboardButton("Нажми меня", callback_data="button_clicked")]
#    ]
#    reply_markup = InlineKeyboardMarkup(keyboard)
#    await update.message.reply_text("Привет! Нажми на кнопку:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()
    
    logger.info(f"🖱️ Пользователь {user.first_name} нажал кнопку: {query.data}")
    await query.edit_message_text("Кнопка нажата! Спасибо!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    
    logger.info(f"💬 Получен текст от {user.first_name}: {text}")
    
    if text.lower() == 'статистика':
        # Логируем запрос статистики
        logger.info(f"📊 Пользователь {user.first_name} запросил статистику")
        start_time = context.user_data.get('start_time', datetime.now())
        elapsed = datetime.now() - start_time
        await update.message.reply_text(f"Вы в боте уже {elapsed.seconds} секунд")
    else:
        await update.message.reply_text(f"Вы написали: {text}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info(f"❓ Пользователь {user.first_name} запросил помощь")
    await update.message.reply_text("Доступные команды:\n/start - запустить бота\n/help - помощь\n/stats - статистика бота\nПросто напишите 'статистика' для личной статистики")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info(f"📈 Пользователь {user.first_name} запросил общую статистику")
    
    # Здесь можно добавить реальную статистику из базы данных
    await update.message.reply_text(
        "📊 Статистика бота:\n"
        f"• Всего пользователей: {len(context.bot_data.get('users', set()))}\n"
        "• Бот работает нормально"
    )

async def track_new_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отслеживание новых пользователей"""
    if update.message and update.message.new_chat_members:
        for member in update.message.new_chat_members:
            if member.id != context.bot.id:
                logger.info(f"👤 Новый пользователь в чате: {member.first_name} (@{member.username}, id:{member.id})")
                await update.message.reply_text(f"Добро пожаловать, {member.first_name}!")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Логирование ошибок"""
    logger.error(f"❌ Ошибка: {context.error}", exc_info=True)
    if update and update.message:
        await update.message.reply_text("Произошла ошибка. Администратор уже уведомлён.")

def main():
    
    app = Application.builder().token(TOKEN).build()
    
    # Обработчик анкеты
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Анкета$"), survey_start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, survey_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, survey_age)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("inline", inline_buttons))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, track_new_user))
 
    # Глобальный обработчик ошибок
    app.add_error_handler(error_handler)
    
    # Логируем запуск бота
    logger.info("🚀 Бот успешно запущен!")
    logger.info(f"📅 Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()