
import imghdr
import os
from asyncio import gather
from traceback import format_exc

from pyrogram import filters
from pyrogram.errors import (
    PeerIdInvalid,
    ShortnameOccupyFailed,
    StickerEmojiInvalid,
    StickerPngDimensions,
    StickerPngNopng,
    UserIsBlocked,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from LoverCodes import app
from config import BOT_USERNAME
from LoverCodes.utils.errors import capture_err

from LoverCodes.utils.files import (
    get_document_from_file_id,
    resize_file_to_sticker_size,
    upload_document,
)

from LoverCodes.utils.stickerset import (
    add_sticker_to_set,
    create_sticker,
    create_sticker_set,
    get_sticker_set_by_name,
)

from LoverCodes.utils.decorators import language

MAX_STICKERS = (
    120  
)
SUPPORTED_TYPES = ["jpeg", "png", "webp"]
# ------------------------------------------
@app.on_message(filters.command("get_sticker"))
@capture_err
@language
async def sticker_image(client, message: Message, _):
    return await message.reply_text(_["BLOCK_CM"])


@app.on_message(filters.command("kang"))
@capture_err
@language
async def kang(client, message: Message, _):
    return await message.reply_text(_["BLOCK_CM"])
