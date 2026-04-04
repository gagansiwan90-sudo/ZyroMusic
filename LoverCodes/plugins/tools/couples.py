import os 
import random
from datetime import datetime 
from telegraph import upload_file
from PIL import Image , ImageDraw
from pyrogram import *
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import *

#BOT FILE NAME
from LoverCodes import app as app
from LoverCodes.mongo.couples_db import _get_image, get_couple

POLICE = [
    [
        InlineKeyboardButton(
            text="𓊈𒆜彡[𝐃𝚊𝚡𝚡 𝐂𝙲 𝐂𝙻𝚄𝙱 ]彡𒆜𓊉",
            url=f"https://t.me/ALLTYPECC",
        ),
    ],
]


def dt():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M")
    dt_list = dt_string.split(" ")
    return dt_list
    

def dt_tom():
    a = (
        str(int(dt()[0].split("/")[0]) + 1)
        + "/"
        + dt()[0].split("/")[1]
        + "/"
        + dt()[0].split("/")[2]
    )
    return a

tomorrow = str(dt_tom())
today = str(dt()[0])



from LoverCodes.utils.decorators import language

@app.on_message(filters.command("couples"))
@language
async def ctest(client, message, _):

    return await message.reply_text(_["BLOCK_CM"])



__mod__ = "COUPLES"
__help__ = """
**» /couples** - Get Todays Couples Of The Group In Interactive View
"""





    




    
