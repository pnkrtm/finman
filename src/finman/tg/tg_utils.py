import os
import secrets
import tempfile

from loguru import logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from src.finman.exceptions.base import FinManBaseException
from src.finman.pipeline import ProcessPipeline

START_STATE = 0
CONFIGURE_START_STATE = 0

START_CALLBACK_1, START_CALLBACK_2 = range(2)


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


async def start_configure(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Please, send me *.json file with configuration")

    return CONFIGURE_START_STATE


async def process_configuration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        logger.debug("Configuration started...")

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_file = os.path.join(tmp_dir, f"{secrets.token_hex(nbytes=16)}")

            new_file = await update.message.effective_attachment.get_file()
            await new_file.download_to_drive(tmp_file)

            pipeline = ProcessPipeline()
            pipeline.configure(filename=tmp_file)

        logger.debug("Configuration has been finished!")

        await update.message.reply_text(f"Configuration successfully done!")
        return ConversationHandler.END

    except FinManBaseException as e:
        await update.message.reply_text(f"Problems while configuration: {str(e)}")
        return ConversationHandler.END

    except Exception as e:
        logger.opt(exception=e).info("Logging exception traceback")
        await update.message.reply_text(f"Unknown problem while configuration: {str(e)}")
        return ConversationHandler.END


async def cancel_configuration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(f"Configuration cancelled")

    return ConversationHandler.END
