# Copyright (C) @TheSmartBisnu
# Channel: https://t.me/itsSmartDev

import os
from time import time
from pyrogram import enums
from pyleaves import Leaves
from collections import defaultdict
from pyrogram.types import InputMediaPhoto, InputMediaVideo

# Maximum file size limit to 2GB
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # If your telegram account is premium then use 4GB

def chkFileSize(file_size):
    return file_size <= MAX_FILE_SIZE

async def fileSizeLimit(file_size, message, action_type="download"):
    if not chkFileSize(file_size):
        await message.reply(f"The file size exceeds the {MAX_FILE_SIZE / (1024 * 1024 * 1024):.2f}GB limit and cannot be {action_type}ed.")
        return False
    return True

priority = {
    enums.MessageEntityType.BOLD: 1,
    enums.MessageEntityType.ITALIC: 2,
    enums.MessageEntityType.UNDERLINE: 3,
    enums.MessageEntityType.STRIKETHROUGH: 4,
    enums.MessageEntityType.SPOILER: 5,
    enums.MessageEntityType.CODE: 6,
    enums.MessageEntityType.PRE: 7,
    enums.MessageEntityType.TEXT_LINK: 8,
    enums.MessageEntityType.HASHTAG: 9
}

default_priority = 100

async def get_parsed_msg(message_text, entities):
    if not entities:
        return message_text

    entity_dict = defaultdict(list)
    for entity in entities:
        start = entity.offset
        end = entity.offset + entity.length
        entity_dict[(start, end)].append(entity)

    last_end = 0
    result = []
    for (start, end), entities in sorted(entity_dict.items()):
        if start > last_end:
            result.append(message_text[last_end:start])
        formatted_text = message_text[start:end]
        entities.sort(key=lambda x: priority.get(x.type, default_priority), reverse=True)
        for entity in entities:
            if entity.type == enums.MessageEntityType.BOLD:
                formatted_text = f"**{formatted_text}**"
            elif entity.type == enums.MessageEntityType.ITALIC:
                formatted_text = f"__{formatted_text}__"
            elif entity.type == enums.MessageEntityType.UNDERLINE:
                formatted_text = f"--{formatted_text}--"
            elif entity.type == enums.MessageEntityType.STRIKETHROUGH:
                formatted_text = f"~~{formatted_text}~~"
            elif entity.type == enums.MessageEntityType.SPOILER:
                formatted_text = f"||{formatted_text}||"
            elif entity.type == enums.MessageEntityType.CODE:
                formatted_text = f"`{formatted_text}`"
            elif entity.type == enums.MessageEntityType.PRE:
                formatted_text = f"```{formatted_text}```"
            elif entity.type == enums.MessageEntityType.TEXT_LINK:
                formatted_text = f"[{formatted_text}]({entity.url})"
            elif entity.type == enums.MessageEntityType.HASHTAG:
                formatted_text = f"{formatted_text}"

        result.append(formatted_text)
        last_end = end

    if last_end < len(message_text):
        result.append(message_text[last_end:])

    return "".join(result)


# Progress bar template
PROGRESS_BAR = """
Percentage: {percentage:.2f}% | {current}/{total}
Speed: {speed}/s
Estimated Time Left: {est_time} seconds
"""

# Function to extract chat ID and message ID from URL
def getChatMsgID(url: str):
    parts = url.split("/")
    chat_id = int("-100" + parts[-2])
    message_id = int(parts[-1])
    return chat_id, message_id
    
    
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

# Helper function to handle media groups
async def processMediaGroup(user, chat_id, message_id, bot, message):
    media_group_messages = await user.get_media_group(chat_id, message_id)
    media_list = []

    for msg in media_group_messages:
        if msg.photo:
            media_list.append(InputMediaPhoto(media=msg.photo.file_id, caption=await get_parsed_msg(msg.caption or "", msg.caption_entities)))
        elif msg.video:
            media_list.append(InputMediaVideo(media=msg.video.file_id, caption=await get_parsed_msg(msg.caption or "", msg.caption_entities)))

    if media_list:
        await bot.send_media_group(chat_id=message.chat.id, media=media_list)
        return True
    return False
