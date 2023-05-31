import tempfile

from loguru import logger
from telegram import Update
from telegram.ext import BaseHandler, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from src.finman.pipeline import ProcessPipeline
from src.finman.tg._utils import download_tmp_file

CONFIGURE_START_STATE = 0


def get_configure_handler() -> BaseHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("start_configuration", start_configure)],
        states={CONFIGURE_START_STATE: [MessageHandler(filters.Document.FileExtension("json"), process_configuration)]},
        fallbacks=[CommandHandler("cancel_configuration", cancel_configuration)],
    )


async def start_configure(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Please, send me *.json file with configuration")

    return CONFIGURE_START_STATE


async def process_configuration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.debug("Configuration started...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        pipeline = ProcessPipeline()
        tmp_filename = await download_tmp_file(tmp_dir, update)
        result = pipeline.configure(filename=tmp_filename)

    if result["success"]:
        logger.debug("Configuration has been finished!")

        await update.message.reply_text(f"Configuration successfully done!")
        return ConversationHandler.END

    else:
        await update.message.reply_text(result["reason"] + ": " + result["message"])
        return ConversationHandler.END


async def cancel_configuration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(f"Configuration cancelled")

    return ConversationHandler.END
