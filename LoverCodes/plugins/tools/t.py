from pyrogram import Client, filters, enums
from pyrogram.types import Message
from LoverCodes import app

@app.on_message(filters.command("pid"))
async def get_pid(client: Client, message: Message):
    target = message.reply_to_message if message.reply_to_message else message

    unique_emojis = {}

    text = target.text or target.caption
    entities = target.entities or target.caption_entities or []

    if text:
        for entity in entities:
            if entity.type == enums.MessageEntityType.CUSTOM_EMOJI:
                emoji_id = entity.custom_emoji_id

                if emoji_id not in unique_emojis:
                    try:
                        emoji_char = text[entity.offset: entity.offset + entity.length]
                    except Exception:
                        emoji_char = "💎"

                    html_tag = f"<emoji id=\"{emoji_id}\">{emoji_char}</emoji>"
                    markdown_tag = f"![{emoji_char}](tg://emoji?id={emoji_id})"

                    entry = (
                        f"<b>Preview :</b> <emoji id=\"{emoji_id}\">{emoji_char}</emoji>\n"
                        f"<b>Emoji ID :</b> <code>{emoji_id}</code>\n"
                        f"<b>Example :</b>\n"
                        f"<b>HTML :</b> <code>{html_tag}</code>\n"
                        f"<b>MARKDOWN :</b> <code>{markdown_tag}</code>"
                    )

                    unique_emojis[emoji_id] = entry

                    if len(unique_emojis) >= 15:
                        break

    elif entities:
        for entity in entities:
            if entity.type == enums.MessageEntityType.CUSTOM_EMOJI:
                emoji_id = entity.custom_emoji_id

                if emoji_id not in unique_emojis:
                    html_tag = f"<emoji id=\"{emoji_id}\">💎</emoji>"
                    markdown_tag = f"![💎](tg://emoji?id={emoji_id})"

                    entry = (
                        f"<b>Preview :</b> <emoji id=\"{emoji_id}\">💎</emoji>\n"
                        f"<b>Emoji ID :</b> <code>{emoji_id}</code>\n"
                        f"<b>Example :</b>\n"
                        f"<b>HTML :</b> <code>{html_tag}</code>\n"
                        f"<b>MARKDOWN :</b> <code>{markdown_tag}</code>"
                    )

                    unique_emojis[emoji_id] = entry

                    if len(unique_emojis) >= 15:
                        break

    # Sticker check
    if len(unique_emojis) < 15:
        if target.sticker and target.sticker.custom_emoji_id:
            emoji_id = target.sticker.custom_emoji_id

            if emoji_id not in unique_emojis:
                html_tag = f"<emoji id=\"{emoji_id}\">💎</emoji>"
                markdown_tag = f"![💎](tg://emoji?id={emoji_id})"

                entry = (
                    f"<b>Preview :</b> <emoji id=\"{emoji_id}\">💎</emoji> (Sticker)\n"
                    f"<b>Emoji ID :</b> <code>{emoji_id}</code>\n"
                    f"<b>Example :</b>\n"
                    f"<b>HTML :</b> <code>{html_tag}</code>\n"
                    f"<b>MARKDOWN :</b> <code>{markdown_tag}</code>"
                )

                unique_emojis[emoji_id] = entry

    # Animation check
    if len(unique_emojis) < 15:
        if target.animation and target.animation.custom_emoji_id:
            emoji_id = target.animation.custom_emoji_id

            if emoji_id not in unique_emojis:
                html_tag = f"<emoji id=\"{emoji_id}\">💎</emoji>"
                markdown_tag = f"![💎](tg://emoji?id={emoji_id})"

                entry = (
                    f"<b>Preview :</b> <emoji id=\"{emoji_id}\">💎</emoji> (Animation)\n"
                    f"<b>Emoji ID :</b> <code>{emoji_id}</code>\n"
                    f"<b>Example :</b>\n"
                    f"<b>HTML :</b> <code>{html_tag}</code>\n"
                    f"<b>MARKDOWN :</b> <code>{markdown_tag}</code>"
                )

                unique_emojis[emoji_id] = entry

    if not unique_emojis:
        if message.reply_to_message:
            await message.reply_text("No premium emojis found in the replied message.")
        else:
            await message.reply_text(
                "Reply to a message with premium emojis or send emojis with /pid."
            )
        return

    res = "<b>Extracted Premium Emojis:</b>\n"
    res += "\n────────────────────\n".join(unique_emojis.values())

    if len(unique_emojis) >= 15:
        res += "\n\n<i>(Showing first 15 emojis)</i>"

    res += "\n\n<i>Copy the ID to use in filters.</i>"

    await target.reply_text(res, parse_mode=enums.ParseMode.HTML)
