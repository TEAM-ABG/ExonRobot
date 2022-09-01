"""
MIT License

Copyright (c) 2022 Aʙɪsʜɴᴏɪ

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import html
from typing import Optional

from telegram import Chat, ChatPermissions, Message, ParseMode, Update, User
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler
from telegram.utils.helpers import mention_html, mention_markdown

import Exon.modules.sql.blsticker_sql as sql
from Exon import LOGGER, dispatcher
from Exon.modules.connection import connected
from Exon.modules.disable import DisableAbleCommandHandler
from Exon.modules.helper_funcs.alternate import send_message
from Exon.modules.helper_funcs.chat_status import user_admin, user_not_admin
from Exon.modules.helper_funcs.misc import split_message
from Exon.modules.helper_funcs.string_handling import extract_time
from Exon.modules.log_channel import loggable
from Exon.modules.sql.approve_sql import is_approved
from Exon.modules.warns import warn


def blackliststicker(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    bot, args = context.bot, context.args
    if conn := connected(bot, update, chat, user.id, need_admin=False):
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if chat.type == "private":
            return
        chat_id = update.effective_chat.id
        chat_name = chat.title

    sticker_list = f"<b>ʟɪsᴛ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ sᴛɪᴄᴋᴇʀs ᴄᴜʀʀᴇɴᴛʟʏ ɪɴ {chat_name}:</b>\n"

    all_stickerlist = sql.get_chat_stickers(chat_id)

    if len(args) > 0 and args[0].lower() == "copy":
        for trigger in all_stickerlist:
            sticker_list += f"<code>{html.escape(trigger)}</code>\n"
    elif len(args) == 0:
        for trigger in all_stickerlist:
            sticker_list += f" - <code>{html.escape(trigger)}</code>\n"

    split_text = split_message(sticker_list)
    for text in split_text:
        if (
            sticker_list
            == f"<b>ʟɪsᴛ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ sᴛɪᴄᴋᴇʀs ᴄᴜʀʀᴇɴᴛʟʏ ɪɴ {chat_name}:</b>\n".format(
                html.escape(chat_name)
            )
        ):
            send_message(
                update.effective_message,
                f"ᴛʜᴇʀᴇ ᴀʀᴇ ɴᴏ ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀs ɪɴ <b>{html.escape(chat_name)}</b>!",
                parse_mode=ParseMode.HTML,
            )

            return
    send_message(update.effective_message, text, parse_mode=ParseMode.HTML)


@user_admin
def add_blackliststicker(update: Update, context: CallbackContext):
    bot = context.bot
    msg = update.effective_message  # type: Optional[Message]
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    words = msg.text.split(None, 1)
    bot = context.bot
    if conn := connected(bot, update, chat, user.id):
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            return
        chat_name = chat.title

    if len(words) > 1:
        text = words[1].replace("https://t.me/addstickers/", "")
        to_blacklist = list(
            {trigger.strip() for trigger in text.split("\n") if trigger.strip()},
        )

        added = 0
        for trigger in to_blacklist:
            try:
                bot.getStickerSet(trigger)
                sql.add_to_stickers(chat_id, trigger.lower())
                added += 1
            except BadRequest:
                send_message(
                    update.effective_message,
                    f"sᴛɪᴄᴋᴇʀ `{trigger}` ᴄᴀɴ ɴᴏᴛ ʙᴇ ғᴏᴜɴᴅ!",
                    parse_mode="markdown",
                )

        if added == 0:
            return

        if len(to_blacklist) == 1:
            send_message(
                update.effective_message,
                f"sᴛɪᴄᴋᴇʀ <code>{html.escape(to_blacklist[0])}</code> ᴀᴅᴅᴇᴅ ᴛᴏ ʙʟᴀᴄᴋʟɪsᴛ sᴛɪʏᴄᴋᴇʀs ɪɴ <b>{html.escape(chat_name)}</b>!",
                parse_mode=ParseMode.HTML,
            )

        else:
            send_message(
                update.effective_message,
                f"<code>{added}</code> sᴛɪᴄᴋᴇʀs ᴀᴅᴅᴇᴅ ᴛᴏ ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀ ɪɴ <b>{html.escape(chat_name)}</b>!",
                parse_mode=ParseMode.HTML,
            )

    elif msg.reply_to_message:
        added = 0
        trigger = msg.reply_to_message.sticker.set_name
        if trigger is None:
            send_message(update.effective_message, "sᴛɪᴄᴋᴇʀ ɪs ɪɴᴠᴀʟɪᴅ!")
            return
        try:
            bot.getStickerSet(trigger)
            sql.add_to_stickers(chat_id, trigger.lower())
            added += 1
        except BadRequest:
            send_message(
                update.effective_message,
                f"sᴛɪᴄᴋᴇʀ `{trigger}` ᴄᴀɴ ɴᴏᴛ ʙᴇ ғᴏᴜɴᴅ!",
                parse_mode="markdown",
            )

        if added == 0:
            return

        send_message(
            update.effective_message,
            f"Sticker <code>{trigger}</code> ᴀᴅᴅᴇᴅ ᴛᴏ ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀs ɪɴ <b>{html.escape(chat_name)}</b>!",
            parse_mode=ParseMode.HTML,
        )

    else:
        send_message(
            update.effective_message,
            "ᴛᴇʟʟ ᴍᴇ ᴡʜᴀᴛ sᴛɪᴄᴋᴇʀs ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴀᴅᴅ ᴛᴏ ᴛʜᴇ ʙʟᴀᴄᴋʟɪsᴛ.",
        )


@user_admin
def unblackliststicker(update: Update, context: CallbackContext):
    bot = context.bot
    msg = update.effective_message  # type: Optional[Message]
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    words = msg.text.split(None, 1)
    bot = context.bot
    if conn := connected(bot, update, chat, user.id):
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            return
        chat_name = chat.title

    if len(words) > 1:
        text = words[1].replace("https://t.me/addstickers/", "")
        to_unblacklist = list(
            {trigger.strip() for trigger in text.split("\n") if trigger.strip()},
        )

        successful = 0
        for trigger in to_unblacklist:
            success = sql.rm_from_stickers(chat_id, trigger.lower())
            if success:
                successful += 1

        if len(to_unblacklist) == 1:
            if successful:
                send_message(
                    update.effective_message,
                    f"sᴛɪᴄᴋᴇʀ <code>{html.escape(to_unblacklist[0])}</code> ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ʙʟᴀᴄᴋʟɪsᴛ ɪɴ <b>{html.escape(chat_name)}</b>!",
                    parse_mode=ParseMode.HTML,
                )

            else:
                send_message(
                    update.effective_message,
                    "ᴛʜɪs sᴛɪᴄᴋᴇʀ ɪs ɴᴏᴛ ᴏɴ ᴛʜᴇ ʙʟᴀᴄᴋʟɪsᴛ...!",
                )

        elif successful == len(to_unblacklist):
            send_message(
                update.effective_message,
                f"sᴛɪᴄᴋᴇʀ <code>{successful}</code> ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ʙʟᴀᴄᴋʟɪsᴛ ɪɴ <b>{html.escape(chat_name)}</b>!",
                parse_mode=ParseMode.HTML,
            )

        elif not successful:
            send_message(
                update.effective_message,
                "ɴᴏɴᴇ ᴏғ ᴛʜᴇsᴇ sᴛɪᴄᴋᴇʀs ᴇxɪsᴛ, sᴏ ᴛʜᴇʏ ᴄᴀɴɴᴏᴛ ʙᴇ ʀᴇᴍᴏᴠᴇᴅ.",
                parse_mode=ParseMode.HTML,
            )

        else:
            send_message(
                update.effective_message,
                f"sᴛɪᴄᴋᴇʀ <code>{successful}</code> ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ʙʟᴀᴄᴋʟɪsᴛ. {len(to_unblacklist) - successful} ᴅɪᴅ ɴᴏᴛ ᴇxɪsᴛ, sᴏ ɪᴛ's ɴᴏᴛ ᴅᴇʟᴇᴛᴇᴅ.",
                parse_mode=ParseMode.HTML,
            )

    elif msg.reply_to_message:
        trigger = msg.reply_to_message.sticker.set_name
        if trigger is None:
            send_message(update.effective_message, "sᴛɪᴄᴋᴇʀ ɪs ɪɴᴠᴀʟɪᴅ!")
            return
        if success := sql.rm_from_stickers(chat_id, trigger.lower()):
            send_message(
                update.effective_message,
                f"sᴛɪᴄᴋᴇʀ <code>{trigger}</code> ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ʙʟᴀᴄᴋʟɪsᴛ ɪɴ <b>{chat_name}</b>!",
                parse_mode=ParseMode.HTML,
            )

        else:
            send_message(
                update.effective_message,
                f"{trigger} ɴᴏᴛ ғᴏᴜɴᴅ ᴏɴ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ sᴛɪᴄᴋᴇʀs...!",
            )

    else:
        send_message(
            update.effective_message,
            "ᴛᴇʟʟ ᴍᴇ ᴡʜᴀᴛ sᴛɪᴄᴋᴇʀs ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʀᴇᴍᴏᴠᴇ ғʀᴏᴍ ᴛʜᴇ ʙʟᴀᴄᴋʟɪsᴛ.",
        )


@loggable
@user_admin
def blacklist_mode(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]
    bot, args = context.bot, context.args
    conn = connected(bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = dispatcher.bot.getChat(conn)
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(
                update.effective_message,
                "ʏᴏᴜ ᴄᴀɴ ᴅᴏ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪɴ ɢʀᴏᴜᴘ's, ɴᴏᴛ PM",
            )
            return ""
        chat = update.effective_chat
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if args:
        if args[0].lower() in ["off", "nothing", "no"]:
            settypeblacklist = "ᴛᴜʀɴ ᴏғғ"
            sql.set_blacklist_strength(chat_id, 0, "0")
        elif args[0].lower() in ["del", "delete"]:
            settypeblacklist = "ʟᴇғᴛ, ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ"
            sql.set_blacklist_strength(chat_id, 1, "0")
        elif args[0].lower() == "warn":
            settypeblacklist = "ᴡᴀʀɴᴇᴅ"
            sql.set_blacklist_strength(chat_id, 2, "0")
        elif args[0].lower() == "mute":
            settypeblacklist = "ᴍᴜᴛᴇᴅ"
            sql.set_blacklist_strength(chat_id, 3, "0")
        elif args[0].lower() == "kick":
            settypeblacklist = "ᴋɪᴄᴋᴇᴅ"
            sql.set_blacklist_strength(chat_id, 4, "0")
        elif args[0].lower() == "ban":
            settypeblacklist = "ʙᴀɴɴᴇᴅ"
            sql.set_blacklist_strength(chat_id, 5, "0")
        elif args[0].lower() == "ᴛʙᴀɴ":
            if len(args) == 1:
                teks = """ɪᴛ ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ᴀʀᴇ ᴛʀʏɪɴɢ ᴛᴏ sᴇᴛ ᴀ ᴛᴇᴍᴘᴏʀᴀʀʏ ᴠᴀʟᴜᴇ ᴛᴏ ʙʟᴀᴄᴋʟɪsᴛ, ʙᴜᴛ ʜᴀs ɴᴏᴛ ᴅᴇᴛᴇʀᴍɪɴᴇᴅ ᴛʜᴇ ᴛɪᴍᴇ; ᴜsᴇ `/blstickermode tban <timevalue>`.
                                              ᴇxᴀᴍᴘʟᴇs ᴏғ ᴛɪᴍᴇ ᴠᴀʟᴜᴇs : 4ᴍ = 4 ᴍɪɴᴜᴛᴇ, 3ʜ = 3 ʜᴏᴜʀs, 6ᴅ = 6 ᴅᴀʏs, 5w = 5 ᴡᴇᴇᴋs."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return
            settypeblacklist = f"ᴛᴇᴍᴘᴏʀᴀʀʏ ʙᴀɴɴᴇᴅ ғᴏʀ {args[1]}"
            sql.set_blacklist_strength(chat_id, 6, str(args[1]))
        elif args[0].lower() == "tmute":
            if len(args) == 1:
                teks = """ɪᴛ ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ᴀʀᴇ ᴛʀʏɪɴɢ ᴛᴏ sᴇᴛ ᴀ ᴛᴇᴍᴘᴏʀᴀʀʏ ᴠᴀʟᴜᴇ ᴛᴏ ʙʟᴀᴄᴋʟɪsᴛ, ʙᴜᴛ ʜᴀs ɴᴏᴛ ᴅᴇᴛᴇʀᴍɪɴᴇᴅ ᴛʜᴇ ᴛɪᴍᴇ; ᴜsᴇ `/blstickermode tmute <timevalue>`.
                                              ᴇxᴀᴍᴘʟᴇs ᴏғ ᴛɪᴍᴇ ᴠᴀʟᴜᴇs: 4ᴍ = 4 ᴍɪɴᴜᴛᴇ, 3ʜ = 3 ʜᴏᴜʀs, 6ᴅ = 6 days, 5ᴡ = 5 ᴡᴇᴇᴋs."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return
            settypeblacklist = f"ᴛᴇᴍᴘᴏʀᴀʀʏ ᴍᴜᴛᴇᴅ ғᴏʀ {args[1]}"
            sql.set_blacklist_strength(chat_id, 7, str(args[1]))
        else:
            send_message(
                update.effective_message,
                "I ᴏɴʟʏ ᴜɴᴅᴇʀsᴛᴀɴᴅ :  off/del/warn/ban/kick/mute/tban/tmute!",
            )
            return
        if conn:
            text = f"ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀ ᴍᴏᴅᴇ ᴄʜᴀɴɢᴇᴅ, ᴜsᴇʀs ᴡɪʟʟ ʙᴇ `{settypeblacklist}` ᴀᴛ *{chat_name}*!"

        else:
            text = (
                f"ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀ ᴍᴏᴅᴇ ᴄʜᴀɴɢᴇᴅ, ᴜsᴇʀs ᴡɪʟʟ ʙᴇ `{settypeblacklist}`!"
            )
        send_message(update.effective_message, text, parse_mode="markdown")
        return f"<b>{html.escape(chat.title)}:</b>\n<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\nᴄʜᴀɴɢᴇᴅ sᴛɪᴄᴋᴇʀ ʙʟᴀᴄᴋʟɪsᴛ ᴍᴏᴅᴇ. ᴜsᴇʀs ᴡɪʟʟ ʙᴇ {settypeblacklist}."

    getmode, getvalue = sql.get_blacklist_setting(chat.id)
    if getmode == 0:
        settypeblacklist = "ɴᴏᴛ ᴀᴄᴛɪᴠᴇ"
    elif getmode == 1:
        settypeblacklist = "ᴅᴇʟᴇᴛᴇ"
    elif getmode == 2:
        settypeblacklist = "ᴡᴀʀɴ"
    elif getmode == 3:
        settypeblacklist = "ᴍᴜᴛᴇ"
    elif getmode == 4:
        settypeblacklist = "ᴋɪᴄᴋ"
    elif getmode == 5:
        settypeblacklist = "ʙᴀɴ"
    elif getmode == 6:
        settypeblacklist = f"ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ʙᴀɴɴᴇᴅ ғᴏʀ {getvalue}"
    elif getmode == 7:
        settypeblacklist = f"ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ᴍᴜᴛᴇᴅ ғᴏʀ {getvalue}"
    if conn:
        text = f"ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀ ᴍᴏᴅᴇ ɪs ᴄᴜʀʀᴇɴᴛʟʏ sᴇᴛ ᴛᴏ *{settypeblacklist}* ɪɴ *{chat_name}*."

    else:
        text = f"ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀ ᴍᴏᴅᴇ ɪs ᴄᴜʀʀᴇɴᴛʟʏ sᴇᴛ ᴛᴏ *{settypeblacklist}*."
    send_message(update.effective_message, text, parse_mode=ParseMode.MARKDOWN)
    return ""


@user_not_admin
def del_blackliststicker(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message  # type: Optional[Message]
    user = update.effective_user
    to_match = message.sticker

    if not to_match or not to_match.set_name:
        return

    if is_approved(chat.id, user.id):  # ignore approved users
        return

    getmode, value = sql.get_blacklist_setting(chat.id)

    chat_filters = sql.get_chat_stickers(chat.id)
    for trigger in chat_filters:
        if to_match.set_name.lower() == trigger.lower():
            try:
                if getmode == 0:
                    return
                if getmode == 1:
                    message.delete()
                elif getmode == 2:
                    message.delete()
                    warn(
                        update.effective_user,
                        chat,
                        f"ᴜsɪɴɢ sᴛɪᴄᴋᴇʀ '{trigger}' ᴡʜɪᴄʜ ɪɴ ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀs",
                        message,
                        update.effective_user,
                    )

                    return
                elif getmode == 3:
                    message.delete()
                    bot.restrict_chat_member(
                        chat.id,
                        update.effective_user.id,
                        permissions=ChatPermissions(can_send_messages=False),
                    )
                    bot.sendMessage(
                        chat.id,
                        f"{mention_markdown(user.id, user.first_name)} ᴍᴜᴛᴇᴅ ʙᴇᴄᴀᴜsᴇ ᴜsɪɴɢ '{trigger}' ᴡʜɪᴄʜ ɪɴ ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀs",
                        parse_mode="markdown",
                    )

                    return
                elif getmode == 4:
                    message.delete()
                    if res := chat.unban_member(update.effective_user.id):
                        bot.sendMessage(
                            chat.id,
                            f"{mention_markdown(user.id, user.first_name)} ᴋɪᴄᴋᴇᴅ ʙᴇᴄᴀᴜsᴇ ᴜsɪɴɢ '{trigger}' ᴡʜɪᴄʜ ɪɴ ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀs",
                            parse_mode="markdown",
                        )

                    return
                elif getmode == 5:
                    message.delete()
                    chat.ban_member(user.id)
                    bot.sendMessage(
                        chat.id,
                        f"{mention_markdown(user.id, user.first_name)} ʙᴀɴɴᴇᴅ ʙᴇᴄᴀᴜsᴇ ᴜsɪɴɢ '{trigger}' ᴡʜɪᴄʜ ɪɴ ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀs",
                        parse_mode="markdown",
                    )

                    return
                elif getmode == 6:
                    message.delete()
                    bantime = extract_time(message, value)
                    chat.ban_member(user.id, until_date=bantime)
                    bot.sendMessage(
                        chat.id,
                        f"{mention_markdown(user.id, user.first_name)} ʙᴀɴɴᴇᴅ ғᴏʀ {value} ʙᴇᴄᴀᴜsᴇ ᴜsɪɴɢ '{trigger}' ᴡʜɪᴄʜ ɪɴ ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀs",
                        parse_mode="markdown",
                    )

                    return
                elif getmode == 7:
                    message.delete()
                    mutetime = extract_time(message, value)
                    bot.restrict_chat_member(
                        chat.id,
                        user.id,
                        permissions=ChatPermissions(can_send_messages=False),
                        until_date=mutetime,
                    )
                    bot.sendMessage(
                        chat.id,
                        f"{mention_markdown(user.id, user.first_name)} ᴍᴜᴛᴇᴅ ғᴏʀ {value} ʙᴇᴄᴀᴜsᴇ ᴜsɪɴɢ '{trigger}' ᴡʜɪᴄʜ ɪɴ ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀs",
                        parse_mode="markdown",
                    )

                    return
            except BadRequest as excp:
                if excp.message != "ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
                    LOGGER.exception("ᴇʀʀᴏʀ ᴡʜɪʟᴇ ᴅᴇʟᴇᴛɪɴɢ ʙʟᴀᴄᴋʟɪsᴛ ᴍᴇssᴀɢᴇ.")
                break


def __import_data__(chat_id, data):
    # set chat blacklist
    blacklist = data.get("sticker_blacklist", {})
    for trigger in blacklist:
        sql.add_to_stickers(chat_id, trigger)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    blacklisted = sql.num_stickers_chat_filters(chat_id)
    return f"ᴛʜᴇʀᴇ ᴀʀᴇ `{blacklisted} `ʙʟᴀᴄᴋʟɪsᴛᴇᴅ sᴛɪᴄᴋᴇʀs."


def __stats__():
    return f"•➥ {sql.num_stickers_filters()} blacklist stickers, across {sql.num_stickers_filter_chats()} ᴄʜᴀᴛs."


__mod_name__ = "𝚂ᴛɪᴄᴋᴇʀs ʙʟᴀᴄᴋʟɪsᴛ 🥷"

BLACKLIST_STICKER_HANDLER = DisableAbleCommandHandler(
    "blsticker",
    blackliststicker,
    admin_ok=True,
    run_async=True,
)
ADDBLACKLIST_STICKER_HANDLER = DisableAbleCommandHandler(
    "addblsticker",
    add_blackliststicker,
    run_async=True,
)
UNBLACKLIST_STICKER_HANDLER = CommandHandler(
    ["unblsticker", "rmblsticker"],
    unblackliststicker,
    run_async=True,
)
BLACKLISTMODE_HANDLER = CommandHandler("blstickermode", blacklist_mode, run_async=True)
BLACKLIST_STICKER_DEL_HANDLER = MessageHandler(
    Filters.sticker & Filters.chat_type.groups,
    del_blackliststicker,
    run_async=True,
)

dispatcher.add_handler(BLACKLIST_STICKER_HANDLER)
dispatcher.add_handler(ADDBLACKLIST_STICKER_HANDLER)
dispatcher.add_handler(UNBLACKLIST_STICKER_HANDLER)
dispatcher.add_handler(BLACKLISTMODE_HANDLER)
dispatcher.add_handler(BLACKLIST_STICKER_DEL_HANDLER)
