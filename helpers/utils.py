# Copyright (C) @TheSmartBisnu
# Channel: https://t.me/itsSmartDev

import re
import os
import logging
from time import time

from pyrogram import enums
from pyleaves import Leaves
from pyrogram.parser import Parser
from collections import defaultdict
from pyrogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAudio

# Maximum file size limit to 2GB
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # If your telegram account is premium then use 4GB

def chkFileSize(file_size):
    return file_size <= MAX_FILE_SIZE

async def fileSizeLimit(file_size, message, action_type="download"):
    if not chkFileSize(file_size):
        await message.reply(f"The file size exceeds the {MAX_FILE_SIZE / (1024 * 1024 * 1024):.2f}GB limit and cannot be {action_type}ed.")
        return False
    return True

async def get_parsed_msg(text, entities):
    return Parser.unparse(text, entities or [], is_html=False)

# Progress bar template
PROGRESS_BAR = """
Percentage: {percentage:.2f}% | {current}/{total}
Speed: {speed}/s
Estimated Time Left: {est_time} seconds
"""

def getChatMsgID(url: str):
    try:
        if "/c/" in url:
            parts = url.split("/")
            chat_id = int("-100" + parts[-2])
            message_id = int(parts[-1])
            return chat_id, message_id

        elif "t.me" in url:
            parts = url.split("/")
            chat_username = parts[-2]
            message_id = int(parts[-1])
            
            return chat_username, message_id

        else:
            raise ValueError("Invalid URL format. Please check the link.")
    
    except (IndexError, ValueError) as e:
        raise ValueError(f"Error parsing URL: {str(e)}")

# Generate progress bar for downloading/uploading
def progressArgs(action: str, progress_message, start_time):
    return (
        action,
        progress_message,
        start_time,
        PROGRESS_BAR,
        '▓',
        '░'
    )

async def send_media(bot, message, media_path, media_type, caption, progress_message, start_time):
    file_size = os.path.getsize(media_path)
    
    if not await fileSizeLimit(file_size, message, "upload"):
        return
    
    progress_args = progressArgs("📥 Uploading Progress", progress_message, start_time)
    print(f"Uploading media: {media_path} ({media_type})")

    if media_type == "photo":
        await message.reply_photo(
            media_path,
            caption=caption or "",
            progress=Leaves.progress_for_pyrogram,
            progress_args=progress_args
        )
    elif media_type == "video":
        await message.reply_video(
            media_path,
            caption=caption or "",
            progress=Leaves.progress_for_pyrogram,
            progress_args=progress_args
        )
    elif media_type == "audio" or media_type == "audio":
        await message.reply_audio(
            media_path,
            caption=caption or "",
            progress=Leaves.progress_for_pyrogram,
            progress_args=progress_args
        )
    elif media_type == "document" or media_type == "document":
        await message.reply_document(
            media_path,
            caption=caption or "",
            progress=Leaves.progress_for_pyrogram,
            progress_args=progress_args
        )

async def processMediaGroup(user, chat_id, message_id, bot, message):
    media_group_messages = await user.get_media_group(chat_id, message_id)
    valid_media = []
    temp_paths = []
    invalid_paths = []

    start_time = time()
    progress_message = await message.reply("📥 Downloading media group...")
    print(f"Downloading media group with {len(media_group_messages)} items...")

    for msg in media_group_messages:
        if msg.photo or msg.video or msg.document or msg.audio or msg.voice:
            try:
                media_path = await msg.download(progress=Leaves.progress_for_pyrogram, progress_args=progressArgs(
                    "📥 Downloading Progress", progress_message, start_time
                ))
                temp_paths.append(media_path)

                if msg.photo:
                    valid_media.append(InputMediaPhoto(media=media_path, caption=await get_parsed_msg(msg.caption or "", msg.caption_entities)))
                elif msg.video:
                    valid_media.append(InputMediaVideo(media=media_path, caption=await get_parsed_msg(msg.caption or "", msg.caption_entities)))
                elif msg.document:
                    valid_media.append(InputMediaDocument(media=media_path, caption=await get_parsed_msg(msg.caption or "", msg.caption_entities)))
                elif msg.audio:
                    valid_media.append(InputMediaAudio(media=media_path, caption=await get_parsed_msg(msg.caption or "", msg.caption_entities)))
                elif msg.voice:
                    valid_media.append(InputMediaVoice(media=media_path, caption=await get_parsed_msg(msg.caption or "", msg.caption_entities)))

            except Exception as e:
                print(f"Error downloading media: {e}")
                if media_path and os.path.exists(media_path):
                    invalid_paths.append(media_path)
                continue

    print(f"Valid media count: {len(valid_media)}")

    if valid_media:
        try:
            await bot.send_media_group(chat_id=message.chat.id, media=valid_media)
            await progress_message.delete()
        except Exception as e:
            await message.reply(f"**❌ Failed to send media group, trying individual uploads**")
            for media in valid_media:
                try:
                    if isinstance(media, InputMediaPhoto):
                        await bot.send_photo(chat_id=message.chat.id, photo=media.media, caption=media.caption)
                    elif isinstance(media, InputMediaVideo):
                        await bot.send_video(chat_id=message.chat.id, video=media.media, caption=media.caption)
                    elif isinstance(media, InputMediaDocument):
                        await bot.send_document(chat_id=message.chat.id, document=media.media, caption=media.caption)
                    elif isinstance(media, InputMediaAudio):
                        await bot.send_audio(chat_id=message.chat.id, audio=media.media, caption=media.caption)
                    elif isinstance(media, InputMediaVoice):
                        await bot.send_voice(chat_id=message.chat.id, voice=media.media, caption=media.caption)
                except Exception as individual_e:
                    await message.reply(f"Failed to upload individual media: {individual_e}")

            await progress_message.delete()

        for path in temp_paths:
            if os.path.exists(path):
                os.remove(path)
        for path in invalid_paths:
            if os.path.exists(path):
                os.remove(path)

        return True

    await progress_message.delete()
    await message.reply("❌ No valid media found in the media group.")
    for path in invalid_paths:
        if os.path.exists(path):
            os.remove(path)
    return False
