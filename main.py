# Copyright (C) @TheSmartBisnu
# Channel: https://t.me/itsSmartDev

import os
from time import time
from pyleaves import Leaves
from pyrogram.types import Message
from pyrogram import Client, filters, enums
from pyrogram.errors import PeerIdInvalid

from helpers.utils import (
    processMediaGroup,
    get_parsed_msg,
    PROGRESS_BAR,
    fileSizeLimit,
    getChatMsgID,
    progressArgs,
    send_media
)

from config import (
    API_ID,
    API_HASH,
    BOT_TOKEN,
    SESSION_STRING
)

# Initialize the bot client
bot = Client(
    "media_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# Client for user session
user = Client(
    "user_session",
    session_string=SESSION_STRING
)

@bot.on_message(filters.command("start") & filters.private)
async def start(bot, message: Message):
    welcome_text = (
        "**👋 Welcome to the Media Downloader Bot!**\n\n"
        "This bot helps you download media from Restricted channel\n"
        "Use /help for more information on how to use this bot."
    )
    await message.reply(welcome_text)

@bot.on_message(filters.command("help") & filters.private)
async def help_command(bot, message: Message):
    help_text = (
        "💡 **How to Use the Bot**\n\n"
        "1. Send the command `/dl post URL` to download media from a specific message.\n"
        "2. The bot will download the media (photos, videos, audio, or documents) also can copy message.\n"
        "3. Make sure the bot and the user client are part of the chat to download the media.\n\n"
        "**Example**: `/dl https://t.me/channelname/123`"
    )
    await message.reply(help_text)

@bot.on_message(filters.command("dl") & filters.private)
async def download_media(bot, message: Message):
    if len(message.command) < 2:
        await message.reply("Provide a post URL after the /dl command.")
        return

    post_url = message.command[1]

    try:
        chat_id, message_id = getChatMsgID(post_url)
        chat_message = await user.get_messages(chat_id, message_id)
        if chat_message.document or chat_message.video or chat_message.audio:
            file_size = chat_message.document.file_size if chat_message.document else \
                        chat_message.video.file_size if chat_message.video else \
                        chat_message.audio.file_size

            if not await fileSizeLimit(file_size, message, "download"):
                return

        parsed_caption = await get_parsed_msg(chat_message.caption or "", chat_message.caption_entities)
        parsed_text = await get_parsed_msg(chat_message.text or "", chat_message.entities)

        if chat_message.media_group_id:
            if not await processMediaGroup(user, chat_id, message_id, bot, message):
                await message.reply("Could not extract any valid media from the media group.")
            return

        elif chat_message.media:
            start_time = time()
            progress_message = await message.reply("Starting...")

            # Proceed with downloading the file
            media_path = await chat_message.download(progress=Leaves.progress_for_pyrogram, progress_args=progressArgs(
                "📥 Downloading Progress", progress_message, start_time
            ))

            media_type = "photo" if chat_message.photo else "video" if chat_message.video else "audio" if chat_message.audio else "document"
            await send_media(bot, message, media_path, media_type, parsed_caption, progress_message, start_time)

            os.remove(media_path)
            await progress_message.delete()

        elif chat_message.text or chat_message.caption:
            await message.reply(parsed_text or parsed_caption)
        else:
            await message.reply("No media or text found in the post URL.")

    except PeerIdInvalid:
        await message.reply("Make sure the user client is part of the chat.")
    except Exception as e:
        error_message = f"Failed to download the media: {str(e)}"
        await message.reply(error_message)

if __name__ == "__main__":
    user.start()
    bot.run()
