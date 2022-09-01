from io import BytesIO

from pyrogram import filters

from Exon import aiohttpsession as aiosession
from Exon import pgram
from Exon.utils.errors import capture_err
from telegram import InlineKeyboardButton, ParseMode, Update 

async def make_carbon(code):
    url = "https://carbonara.vercel.app/api/cook"
    async with aiosession.post(url, json={"code": code}) as resp:
        image = BytesIO(await resp.read())
    image.name = "carbon.png"
    return image


@pgram.on_message(filters.command("carbon"))
@capture_err
async def carbon_func(_, message):
    if not message.reply_to_message:
        return await message.reply_text("`ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴛᴇxᴛ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴄᴀʀʙᴏɴ`")
    if not message.reply_to_message.text:
        return await message.reply_text("`ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴛᴇxᴛ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴄᴀʀʙᴏɴ`")
    m = await message.reply_text("`ɢᴇɴᴇʀᴀᴛɪɴɢ ᴄᴀʀʙᴏɴ...`")
    carbon = await make_carbon(message.reply_to_message.text)
    await m.edit("`waitoo...`")
    await pgram.send_photo(message.chat.id, carbon)
    await m.delete()
    carbon.close()

    
ABISHNOIX = "https://telegra.ph/file/bff9ee4cf39621303e292.jpg"


@pgram.on_message(filters.command("repo"))
async def repo(_, message):
    await message.reply_photo(
        photo=ABISHNOIX,
        caption=f"""✨
** ᴇɴᴊᴏʏ**
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "•ᴍᴜꜱɪᴄ•", url="https://github.com/KingAbishnoi"
                    ),
                    InlineKeyboardButton(
                        "•ʀᴏʙᴏᴠ1•", url="https://github.com/TEAM-ABG/ExonRobot"
                    ),
                ]
            ]
        ),
    )
    
__mod_name__ = "𝙲ᴀʀʙᴏɴ"

__help__ = """

/carbon *:* ᴍᴀᴋᴇs ᴄᴀʀʙᴏɴ ғᴏʀ ʀᴇᴘʟɪᴇᴅ ᴛᴇxᴛ
/repo *:*🌟
 """
