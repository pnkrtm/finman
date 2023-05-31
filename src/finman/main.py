import os

from telegram.ext import Application

from src.finman.tg.configure import get_configure_handler
from src.finman.tg.start import get_starting_handler
from src.finman.tg.statement_process import get_statement_process_handler

TG_TOKEN = os.getenv("TG_TOKEN", None)


def main():
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TG_TOKEN).build()

    # Adding /start command conversation
    application.add_handler(get_starting_handler())

    # Adding /configure command conversation
    application.add_handler(get_configure_handler())

    # Adding statement processing
    application.add_handler(get_statement_process_handler())

    application.run_polling()


if __name__ == "__main__":
    main()
