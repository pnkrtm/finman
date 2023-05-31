from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import BaseHandler, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler

START_STATE = 0
START_CALLBACK_1, START_CALLBACK_2 = range(2)


def get_starting_handler() -> BaseHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_STATE: [
                CallbackQueryHandler(handshake_greet, pattern="^" + str(START_CALLBACK_1) + "$"),
                CallbackQueryHandler(handshake_nice, pattern="^" + str(START_CALLBACK_2) + "$"),
            ]
        },
        fallbacks=[CommandHandler("cancel", handshake_greet)],
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    reply_keyboard = [
        [
            InlineKeyboardButton("You too 😊", callback_data=str(START_CALLBACK_1)),
            InlineKeyboardButton("Fck U 👿", callback_data=str(START_CALLBACK_2)),
        ]
    ]

    await update.message.reply_html(
        rf"Hi {user.mention_html()}! " "I'm a finman bot to help you managing your finances! Nice to meet you:)",
        reply_markup=InlineKeyboardMarkup(reply_keyboard),
    )

    return START_STATE


async def handshake_greet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    await query.message.reply_text("😊")

    return ConversationHandler.END


async def handshake_nice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    user = query.from_user

    await query.message.reply_text(f"Fck U 2 {user.first_name}!")

    return ConversationHandler.END
