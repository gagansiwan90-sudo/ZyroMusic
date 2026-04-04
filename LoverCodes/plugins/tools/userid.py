from LoverCodes import app
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, MessageEntityType

@app.on_message(filters.command("id"))
async def getid(client, message):
    chat = message.chat
    your_id = message.from_user.id
    message_id = message.id
    reply = message.reply_to_message

    text = f"**[ᴍᴇssᴀɢᴇ ɪᴅ:]({message.link})** `{message_id}`\n"
    text += f"**[ʏᴏᴜʀ ɪᴅ:](tg://user?id={your_id})** `{your_id}`\n"

    # Ensure command parsing
    if not message.command:
        message.command = message.text.split()

    # ✅ CHECK FOR CUSTOM EMOJI
    if message.entities:
        for entity in message.entities:
            if entity.type == MessageEntityType.CUSTOM_EMOJI:
                emoji_id = entity.custom_emoji_id
                text += f"**ᴄᴜsᴛᴏᴍ ᴇᴍᴏᴊɪ ɪᴅ:** `{emoji_id}`\n"

    # Normal /id username / user handling
    if len(message.command) == 2:
        try:
            split = message.text.split(None, 1)[1].strip()
            user = await client.get_users(split)
            text += f"**[ᴜsᴇʀ ɪᴅ:](tg://user?id={user.id})** `{user.id}`\n"
        except Exception:
            pass  # Ignore if not a valid user

    text += f"**[ᴄʜᴀᴛ ɪᴅ:]** `{chat.id}`\n\n"

    if (
        reply
        and not getattr(reply, "empty", True)
        and not message.forward_from_chat
        and not reply.sender_chat
        and reply.from_user
    ):
        text += f"**[ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ ɪᴅ:]({reply.link})** `{reply.id}`\n"
        text += f"**[ʀᴇᴘʟɪᴇᴅ ᴜsᴇʀ ɪᴅ:]** `{reply.from_user.id}`\n\n"

    if reply and reply.forward_from_chat:
        text += f"**ғᴏʀᴡᴀʀᴅᴇᴅ ᴄʜᴀᴛ ɪᴅ:** `{reply.forward_from_chat.id}`\n"

    if reply and reply.sender_chat:
        text += f"**sᴇɴᴅᴇʀ ᴄʜᴀᴛ ɪᴅ:** `{reply.sender_chat.id}`\n"

    await message.reply_text(
        text,
        disable_web_page_preview=True,
        parse_mode=ParseMode.DEFAULT,
    )
