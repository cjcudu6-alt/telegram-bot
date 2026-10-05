import telebot
from telebot import types
import requests
import sqlite3

# --- الإعدادات الأساسية ---
API_TOKEN = 'YOUR_BOT_TOKEN_HERE'  # ضع توكن بوتك هنا
API_5SIM_TOKEN = 'YOUR_5SIM_API_TOKEN_HERE'  # ضع مفتاح 5SIM هنا
ADMIN_ID = 6435462563  # الآيدي الخاص بك

bot = telebot.TeleBot(API_TOKEN)

# --- إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 0.0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_user_balance(user_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (user_id, balance) VALUES (?, ?)', (user_id, 0.0))
        conn.commit()
        conn.close()
        return 0.0

def update_user_balance(user_id, amount):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()

# --- لوحة التحكم والأزرار ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🛒 شراء رقم"), types.KeyboardButton("💰 رصيدي"))
    markup.add(types.KeyboardButton("➕ شحن رصيد"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    get_user_balance(user_id)
    bot.reply_to(
        message,
        "مرحباً بك في متجر تفعيل الأرقام الوهمية! 🌐\nاختر ما تحب من القائمة أدناه:",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: message.text == "💰 رصيدي")
def check_balance(message):
    balance = get_user_balance(message.from_user.id)
    bot.reply_to(message, f"رصيدك الحالي هو: **{balance}** روبل", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "➕ شحن رصيد")
def recharge_balance(message):
    recharge_text = (
        "💳 **طرق شحن الرصيد محلياً:**\n\n"
        "1️⃣ **الرمز الخاص بك (تحويل مباشر):**\n"
        "الرمز: `87027606`\n\n"
        "2️⃣ **شام كاش / سيريتل كاش:**\n"
        "قم بالتحويل عبر الرمز أعلاه أو الحساب المعتمد.\n\n"
        "⚠️ **ملاحظة هامة جداً:**\n"
        "بعد إتمام عملية التحويل، أرسل **صورة الإشعار (Screenshot)** مع الـ **ID الخاص بك** إلى الأدمن ليتم شحن رصيدك فوراً:\n"
        "👤 الأدمن: @RAh738"
    )
    bot.reply_to(message, recharge_text, parse_mode="Markdown")

@bot.message_handler(commands=['addbalance'])
def add_balance_admin(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "هذا الأمر مخصص للأدمن فقط.")
        return
    try:
        parts = message.text.split()
        target_user_id = int(parts[1])
        amount = float(parts[2])
        update_user_balance(target_user_id, amount)
        bot.reply_to(message, f"تم بنجاح إضافة {amount} روبل للمستخدم {target_user_id}")
        bot.send_message(target_user_id, f"🎉 تم شحن رصيدك بمقدار {amount} روبل بنجاح!")
    except Exception as e:
        bot.reply_to(message, "خطأ بالصيغة. استخدم الأمر هكذا:\n`/addbalance USER_ID AMOUNT`", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "🛒 شراء رقم")
def buy_number_menu(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("تلغرام (Telegram)", callback_data="buy_telegram"))
    markup.add(types.InlineKeyboardButton("واتساب (WhatsApp)", callback_data="buy_whatsapp"))
    bot.reply_to(message, "اختر التطبيق المطلوب لتفعيل الرقم:", reply_markup=markup)

if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling()
