import aiohttp
from LoverCodes import app
from pyrogram import filters, enums


INFO_TEXT = """**
❅─────✧❅✦❅✧─────❅
            ✦ ᴜsᴇʀ ɪɴғᴏ ✦

➻ ᴜsᴇʀ ɪᴅ ‣ **`{}`  
➻ ғɪʀsᴛ ɴᴀᴍᴇ ‣ **{}  
➻ ʟᴀsᴛ ɴᴀᴍᴇ ‣ **{}  
➻ ᴜsᴇʀɴᴀᴍᴇ ‣ **`{}`  
➻ ᴍᴇɴᴛɪᴏɴ ‣ **{}  
➻ ʟᴀsᴛ sᴇᴇɴ ‣ **{}  
➻ ᴅᴄ ɪᴅ ‣ **{}  
➻ ʙɪᴏ ‣ **`{}`

**❅─────✧❅✦❅✧─────❅**
"""


async def userstatus(user_id):
    try:
        user = await app.get_users(user_id)
        x = user.status

        if x == enums.UserStatus.RECENTLY:
            return "Recently"
        elif x == enums.UserStatus.LAST_WEEK:
            return "Last week"
        elif x == enums.UserStatus.LONG_AGO:
            return "Long time ago"
        elif x == enums.UserStatus.OFFLINE:
            return "Offline"
        elif x == enums.UserStatus.ONLINE:
            return "Online"
        else:
            return "Unknown"
    except:
        return "Unknown"


@app.on_message(filters.command(["info", "userinfo"]))
async def userinfo(_, message):

    # Default → message sender
    user_id = message.from_user.id

    # If replying → target that user
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id

    # If username / id passed
    elif len(message.command) == 2:
        user_id = message.command[1]

    try:
        user_info = await app.get_chat(user_id)
        user = await app.get_users(user_id)
        status = await userstatus(user.id)

        id = user_info.id
        dc_id = user.dc_id
        first_name = user_info.first_name or "None"
        last_name = user_info.last_name or "None"
        username = user_info.username or "None"
        mention = user.mention
        bio = user_info.bio or "No bio set"

        text = INFO_TEXT.format(
            id,
            first_name,
            last_name,
            username,
            mention,
            status,
            dc_id,
            bio,
        )

        await message.reply_text(text, disable_web_page_preview=True)

    except Exception as e:
        await message.reply_text(str(e))
