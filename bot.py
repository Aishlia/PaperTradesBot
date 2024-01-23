from dotenv import load_dotenv
load_dotenv()

import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, filters

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_data[user.id] = {'A': 100, 'B': 0, 'C': 0}
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! You have 100 A tokens.",
        reply_markup=get_keyboard(user.id)
    )

def get_keyboard(user_id):
    keyboard = []
    # Buy buttons
    for token in ['A', 'B', 'C']:
        if user_data[user_id][token] < max(user_data[user_id].values()):
            keyboard.append([InlineKeyboardButton(f"Buy {token} tokens", callback_data=f'buy_{token}')])
    # Sell buttons
    for token in ['A', 'B', 'C']:
        if user_data[user_id][token] > 0:
            keyboard.append([InlineKeyboardButton(f"Sell {token} tokens", callback_data=f'sell_{token}')])

    return InlineKeyboardMarkup(keyboard)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    action, token = query.data.split('_')

    if action == 'buy':
        buy_tokens(user_id, token)
    elif action == 'sell':
        sell_tokens(user_id, token)

    await query.edit_message_text(
        text=f"Transaction complete. Your balance: {user_data[user_id]}",
        reply_markup=get_keyboard(user_id)
    )

def buy_tokens(user_id, token_to_buy):
    for token in ['A', 'B', 'C']:
        if token != token_to_buy and user_data[user_id][token] >= 5:
            user_data[user_id][token] -= 5
            user_data[user_id][token_to_buy] += 5
            break

def sell_tokens(user_id, token_to_sell):
    sell_amount = int(user_data[user_id][token_to_sell] * 0.05)
    user_data[user_id][token_to_sell] -= sell_amount
    for token in ['A', 'B', 'C']:
        if token != token_to_sell:
            user_data[user_id][token] += sell_amount // 2

def main() -> None:
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
