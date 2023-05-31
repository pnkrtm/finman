import os

from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ConversationHandler, MessageHandler, filters

from src.finman.tg.tg_utils import (
    CONFIGURE_START_STATE,
    START_CALLBACK_1,
    START_CALLBACK_2,
    START_STATE,
    cancel_configuration,
    handshake_greet,
    handshake_nice,
    process_configuration,
    start,
    start_configure,
)

TG_TOKEN = os.getenv("TG_TOKEN", None)


def main():
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TG_TOKEN).build()

    # Adding /start command conversation
    application.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                START_STATE: [
                    CallbackQueryHandler(handshake_greet, pattern="^" + str(START_CALLBACK_1) + "$"),
                    CallbackQueryHandler(handshake_nice, pattern="^" + str(START_CALLBACK_2) + "$"),
                ]
            },
            fallbacks=[CommandHandler("cancel", handshake_greet)],
        )
    )

    # Adding /configure command conversation
    application.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("start_configuration", start_configure)],
            states={CONFIGURE_START_STATE: [MessageHandler(filters.Document.FileExtension("json"), process_configuration)]},
            fallbacks=[CommandHandler("cancel_configuration", cancel_configuration)],
        )
    )

    application.run_polling()


if __name__ == "__main__":
    main()
