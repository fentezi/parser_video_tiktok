import asyncio
import logging
import os
import random
import time
from typing import Any

from upload_video.tiktok_uploader import uploadVideo


def get_text_description() -> list:
    with open('upload_video/description.txt', 'r', encoding='utf8') as f:
        lines = f.readlines()
    return lines


async def publish_video(session_id: str) -> bool:
    video_folder = 'video'
    video_files = os.listdir(video_folder)
    description = get_text_description()
    random.shuffle(description)
    video_info = uploadVideo(session_id=session_id,
                             video=f'{video_folder}/{video_files[0]}',
                             title=description[0],
                             tags=[])
    return video_info


async def send_message(message: str, bot: Any) -> None:
    bot.send_message(chat_id='1944331333', text=message)
    logging.info(message)


async def posting_video(session_id: str, bot: Any,
                        sleep_time: float, username: str,
                        number_pc: int, count_publish: int) -> None:
    video_folder = 'video'
    video_files = os.listdir(video_folder)
    video_count = len(video_files)
    if count_publish == 1:
        if video_count > 1:
            video_info = await publish_video(session_id)
            message = (f'#{number_pc}. {username}: {video_files[0]}: {video_info}.'
                       f'Следующая публикация через {time.strftime("%H:%M:%S", time.gmtime(sleep_time))} мин')
            await send_message(message, bot)
        elif video_count == 1:
            video_info = await publish_video(session_id)
            message = f'#{number_pc}. {username}: {video_files[0]}: {video_info}.'
            await send_message(message, bot)
    else:
        for x in range(count_publish):
            video_info = await publish_video(session_id)
            if x == count_publish - 1:
                message = (f'#{number_pc}. {username}: {video_files[0]}: {video_info}.'
                           f' Следующая публикация через {time.strftime("%H:%M:%S", time.gmtime(sleep_time))} мин')
                await send_message(message, bot)
                break
            message = (f'#{number_pc}. {username}: {video_files[0]}: {video_info}.'
                       f' Следующая публикация через 10 сек')
            await send_message(message, bot)
            await asyncio.sleep(10)
    await asyncio.sleep(sleep_time)
    os.remove(f'{video_folder}/{video_files[0]}')
