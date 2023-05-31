import os
import secrets

from telegram import Update


async def download_tmp_file(tmp_dir: str, update: Update) -> str:
    """
    Function for downloading temporary files
    :param tmp_dir: temporary directory
    :param update: telegram update
    :return: name of temporary file
    """
    tmp_file = os.path.join(tmp_dir, f"{secrets.token_hex(nbytes=16)}")

    new_file = await update.message.effective_attachment.get_file()
    await new_file.download_to_drive(tmp_file)

    return tmp_file
