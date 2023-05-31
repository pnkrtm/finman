import tempfile

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import BaseHandler, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from src.finman.pipeline import ProcessPipelineContainer
from src.finman.tg._utils import download_tmp_file

_SWISE_PROCESSING = True

SWISE_YES_CALLBACK, SWISE_NO_CALLBACK = range(2)
START_STATE = 0


def get_statement_process_handler() -> BaseHandler:
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Document.FileExtension("pdf"), ask_swise_processing)],
        states={
            START_STATE: [
                CallbackQueryHandler(process_statement_with_swise, pattern="^" + str(SWISE_YES_CALLBACK) + "$"),
                CallbackQueryHandler(process_statement_without_swise, pattern="^" + str(SWISE_NO_CALLBACK) + "$"),
            ]
        },
        fallbacks=[CommandHandler("cancel_send", cancel_send)],
    )


async def ask_swise_processing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    with tempfile.TemporaryDirectory() as tmp_dir:
        pipeline = ProcessPipelineContainer()[user_id]
        tmp_filename = await download_tmp_file(tmp_dir, update)
        result = pipeline.read_statement(filename=tmp_filename)

        if result["success"]:
            reply_keyboard = [
                [
                    InlineKeyboardButton("Yes", callback_data=str(SWISE_YES_CALLBACK)),
                    InlineKeyboardButton("No", callback_data=str(SWISE_NO_CALLBACK)),
                ]
            ]
            await update.message.reply_html(
                "Do you want to process statement also to Splitwise?",
                reply_markup=InlineKeyboardMarkup(reply_keyboard),
            )
            return START_STATE

        else:
            await update.message.reply_html(result["reason"] + ": " + result["message"])


async def process_statement_with_swise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await _process_statement(update, True)


async def process_statement_without_swise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await _process_statement(update, False)


async def _process_statement(update: Update, use_swise: bool) -> int:
    user_id = update.effective_user.id
    result = ProcessPipelineContainer()[user_id].send_expenses(use_swise)

    if result["success"]:
        query = update.callback_query
        await query.answer()

        await query.message.reply_text(result["output"]["moneywiz_url_schema"])
        await query.message.reply_text("Statement processing successfully finished!")

    else:
        query = update.callback_query
        await query.answer()

        await query.message.reply_text(result["reason"] + ": " + result["message"])
        await query.message.reply_text("Statement processing failed!")

    return ConversationHandler.END


async def cancel_send(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(f"Expense processing cancelled")

    return ConversationHandler.END
