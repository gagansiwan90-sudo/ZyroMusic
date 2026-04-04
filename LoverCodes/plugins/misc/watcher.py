from pyrogram import filters
from pyrogram.types import Message

from LoverCodes import app
from LoverCodes.core.call import Lover

welcome = 20
close = 30

@app.on_message(filters.video_chat_started, group=welcome)
@app.on_message(filters.video_chat_ended, group=close)
async def welcome(_, message: Message):
    await Lover.stop_stream_force(message.chat.id)
