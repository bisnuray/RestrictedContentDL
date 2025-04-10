# Copyright (C) @TheSmartBisnu
# Channel: https://t.me/itsSmartDev

import os
from time import time
from typing import Optional

from pyleaves import Leaves
from pyrogram.parser import Parser
from pyrogram.types import (
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaDocument,
    InputMediaAudio,
    Voice,
)

from logger import LOGGER

SIZE_UNITS = ["B", "KB", "MB", "GB", "TB", "PB"]


def get_readable_file_size(size_in_bytes: Optional[float]) -> str:
    if size_in_bytes is None or size_in_bytes < 0:
        return "0B"

    for unit in SIZE_UNITS:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024

    return "File too large"


def get_readable_time(seconds: int) -> str:
    result = ""
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f"{days}d"
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f"{hours}h"
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f"{minutes}m"
    seconds = int(seconds)
    result += f"{seconds}s"
    return result


async def fileSizeLimit(file_size, message, action_type="download", is_premium=False):
    MAX_FILE_SIZE = 2 * 2097152000 if is_premium else 2097152000
    if file_size > MAX_FILE_SIZE:
        await message.reply(
            f"The file size exceeds the {get_readable_file_size(MAX_FILE_SIZE)} limit and cannot be {action_type}ed."
        )
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
    return (action, progress_message, start_time, PROGRESS_BAR, "▓", "░")


async def send_media(
    bot, message, media_path, media_type, caption, progress_message, start_time
):
    file_size = os.path.getsize(media_path)

    if not await fileSizeLimit(file_size, message, "upload"):
        return

    progress_args = progressArgs("📥 Uploading Progress", progress_message, start_time)
    LOGGER(__name__).info(f"Uploading media: {media_path} ({media_type})")

    if media_type == "photo":
        await message.reply_photo(
            media_path,
            caption=caption or "",
            progress=Leaves.progress_for_pyrogram,
            progress_args=progress_args,
        )
    elif media_type == "video":
        await message.reply_video(
            media_path,
            caption=caption or "",
            progress=Leaves.progress_for_pyrogram,
            progress_args=progress_args,
        )
    elif media_type == "audio":
        await message.reply_audio(
            media_path,
            caption=caption or "",
            progress=Leaves.progress_for_pyrogram,
            progress_args=progress_args,
        )
    elif media_type == "document":
        await message.reply_document(
            media_path,
            caption=caption or "",
            progress=Leaves.progress_for_pyrogram,
            progress_args=progress_args,
        )


async def processMediaGroup(user, chat_id, message_id, bot, message):
    media_group_messages = await user.get_media_group(chat_id, message_id)
    valid_media = []
    temp_paths = []
    invalid_paths = []

    start_time = time()
    progress_message = await message.reply("📥 Downloading media group...")
    LOGGER(__name__).info(
        f"Downloading media group with {len(media_group_messages)} items..."
    )

    for msg in media_group_messages:
        if msg.photo or msg.video or msg.document or msg.audio:
            try:
                media_path = await msg.download(
                    progress=Leaves.progress_for_pyrogram,
                    progress_args=progressArgs(
                        "📥 Downloading Progress", progress_message, start_time
                    ),
                )
                temp_paths.append(media_path)

                if msg.photo:
                    valid_media.append(
                        InputMediaPhoto(
                            media=media_path,
                            caption=await get_parsed_msg(
                                msg.caption or "", msg.caption_entities
                            ),
                        )
                    )
                elif msg.video:
                    valid_media.append(
                        InputMediaVideo(
                            media=media_path,
                            caption=await get_parsed_msg(
                                msg.caption or "", msg.caption_entities
                            ),
                        )
                    )
                elif msg.document:
                    valid_media.append(
                        InputMediaDocument(
                            media=media_path,
                            caption=await get_parsed_msg(
                                msg.caption or "", msg.caption_entities
                            ),
                        )
                    )
                elif msg.audio:
                    valid_media.append(
                        InputMediaAudio(
                            media=media_path,
                            caption=await get_parsed_msg(
                                msg.caption or "", msg.caption_entities
                            ),
                        )
                    )

            except Exception as e:
                LOGGER(__name__).info(f"Error downloading media: {e}")
                if media_path and os.path.exists(media_path):
                    invalid_paths.append(media_path)
                continue

    LOGGER(__name__).info(f"Valid media count: {len(valid_media)}")

    if valid_media:
        try:
            await bot.send_media_group(chat_id=message.chat.id, media=valid_media)
            await progress_message.delete()
        except Exception:
            await message.reply(
                "**❌ Failed to send media group, trying individual uploads**"
            )
            for media in valid_media:
                try:
                    if isinstance(media, InputMediaPhoto):
                        await bot.send_photo(
                            chat_id=message.chat.id,
                            photo=media.media,
                            caption=media.caption,
                        )
                    elif isinstance(media, InputMediaVideo):
                        await bot.send_video(
                            chat_id=message.chat.id,
                            video=media.media,
                            caption=media.caption,
                        )
                    elif isinstance(media, InputMediaDocument):
                        await bot.send_document(
                            chat_id=message.chat.id,
                            document=media.media,
                            caption=media.caption,
                        )
                    elif isinstance(media, InputMediaAudio):
                        await bot.send_audio(
                            chat_id=message.chat.id,
                            audio=media.media,
                            caption=media.caption,
                        )
                    elif isinstance(media, Voice):
                        await bot.send_voice(
                            chat_id=message.chat.id,
                            voice=media.media,
                            caption=media.caption,
                        )
                except Exception as individual_e:
                    await message.reply(
                        f"Failed to upload individual media: {individual_e}"
                    )

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
