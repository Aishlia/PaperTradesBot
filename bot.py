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
    for token in ['A', 'B', 'C']:
        keyboard.append([InlineKeyboardButton(f"Buy {token} tokens", callback_data=f'buy_{token}')])
    # for token in ['A', 'B', 'C']:
    #     if user_data[user_id][token] > 0:
    #         keyboard.append([InlineKeyboardButton(f"Sell {token} tokens", callback_data=f'sell_{token}')])

    return InlineKeyboardMarkup(keyboard)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data_parts = query.data.split('_')

    if data_parts[0] == 'buy':
        await choose_sell_token(update, user_id, data_parts[1])
    elif data_parts[0] == 'sell':
        if len(data_parts) == 5:
            token_to_sell = data_parts[1]
            token_to_buy = data_parts[4]
            buy_tokens(user_id, token_to_sell, token_to_buy)
            await update_user_balance(update, user_id)
        else:
            sell_tokens(user_id, data_parts[1])
            await update_user_balance(update, user_id)


async def choose_sell_token(update: Update, user_id, token_to_buy):
    keyboard = []
    for token in ['A', 'B', 'C']:
        if token != token_to_buy and user_data[user_id][token] > 0:
            keyboard.append([InlineKeyboardButton(f"Sell {token} to buy {token_to_buy}", callback_data=f'sell_{token}_to_buy_{token_to_buy}')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text(
        f"Choose the token to sell in order to buy {token_to_buy} tokens:",
        reply_markup=reply_markup
    )

async def update_user_balance(update: Update, user_id):
    await update.callback_query.message.edit_text(
        text=f"Transaction complete. Your balance: {user_data[user_id]}",
        reply_markup=get_keyboard(user_id)
    )

def buy_tokens(user_id, token_to_sell, token_to_buy):
    sell_amount = 5  # or calculate based on your business logic
    user_data[user_id][token_to_sell] -= sell_amount
    user_data[user_id][token_to_buy] += sell_amount


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
