import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1408724092

PRODUCTS = {
    "pubg": ["60 UC", "325 UC", "660 UC", "1800 UC", "3850 UC"],
    "brawl": ["30 гемов", "80 гемов", "170 гемов", "360 гемов"]
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 PUBG MOBILE", callback_data="pubg")],
        [InlineKeyboardButton("💎 BRAWL STARS", callback_data="brawl")]
    ]
    await update.message.reply_text(
        "🔥 SHOP EVILA 🔥\n\nДобро пожаловать в игровой магазин!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    game = query.data
    context.user_data["game"] = game

    keyboard = [
        [InlineKeyboardButton(item, callback_data=f"buy:{item}")]
        for item in PRODUCTS[game]
    ]

    await query.message.reply_text(
        "Выбери пакет:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["product"] = query.data.split(":", 1)[1]

    game = context.user_data["game"]
    context.user_data["awaiting_id"] = True

    if game == "pubg":
        text = "Отправь свой игровой PUBG Player ID:"
    else:
        text = "Отправь свой игровой Brawl Stars Player Tag:"

    await query.message.reply_text(text)

async def player_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_id"):
        return

    context.user_data["awaiting_id"] = False

    game = context.user_data["game"]
    product = context.user_data["product"]
    player = update.message.text.strip()

    order = (
        f"🛒 НОВЫЙ ЗАКАЗ SHOP EVILA\n\n"
        f"Игра: {game}\n"
        f"Товар: {product}\n"
        f"Игровой ID: {player}\n"
        f"Покупатель: {update.effective_user.id}"
    )

    await update.message.reply_text(
        "✅ Заявка принята!\n"
        "Администратор свяжется с тобой для оплаты и обработки заказа."
    )

    await context.bot.send_message(ADMIN_ID, order)

def main():
    if not TOKEN:
        raise RuntimeError("Не задан BOT_TOKEN")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose, pattern="^(pubg|brawl)$"))
    app.add_handler(CallbackQueryHandler(buy, pattern="^buy:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, player_id))

    app.run_polling()

if __name__ == "__main__":
    main()
