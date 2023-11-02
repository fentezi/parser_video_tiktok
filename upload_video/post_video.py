import logging
import os
import random
import time
from upload_video.tiktok_uploader import uploadVideo
from typing import Any


def get_text_description():
    with open('description.txt', 'r', encoding='utf8') as f:
        lines = f.readlines()
    return lines


async def posting_video(session_id: str, bot: Any, sleep_time: float):
    video_folder = 'video'
    video_files = os.listdir(video_folder)
    video_count = len(video_files)
    if video_count > 1:
        description = get_text_description()
        random.shuffle(description)
        video_info = uploadVideo(session_id=session_id,
                                 video=f'{video_folder}/{video_files[0]}',
                                 title=description[0],
                                 tags=[])
        bot.send_message(chat_id='1944331333',
                         text=f'{video_files[0]}: {video_info}. Следующая публикация через {time.strftime("%H:%M:%S", time.gmtime(sleep_time))} мин')
        logging.info(
            f'{video_files[0]}: {video_info}. Следующая публикация через {time.strftime("%H:%M:%S", time.gmtime(sleep_time))} мин')
        os.remove(f'{video_folder}/{video_files[0]}')
    elif video_count == 1:
        description = get_text_description()
        random.shuffle(description)
        video_info = uploadVideo(session_id=session_id,
                                 video=f'{video_folder}/{video_files[0]}',
                                 title=description[0],
                                 tags=[])
        bot.send_message(chat_id='1944331333',
                         text=f'{video_files[0]}: {video_info}.')
        os.remove(f'{video_folder}/{video_files[0]}')
