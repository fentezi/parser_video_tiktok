import logging
import os
import random
import time

from upload_video.tiktok_uploader import uploadVideo


class FolderIsEmpty(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return f"Folder {self.message} is empty"


def get_text_description():
    with open('description.txt', 'r', encoding='utf8') as f:
        lines = f.readlines()
    return lines


def posting_video(session_id: str, bot):
    try:
        upload_delay = 30
        ty_res = time.gmtime(upload_delay)

        video_folder = 'video'
        video_files = os.listdir(video_folder)
        video_count = len(video_files)
        if video_count >= 1:
            for index in range(video_count):
                description = get_text_description()
                random.shuffle(description)
                video_info = uploadVideo(session_id=session_id,
                                         video=f'{video_folder}/{video_files[index]}',
                                         title=description[0],
                                         tags=[])
                if index == video_count - 1:
                    bot.send_message(chat_id='1944331333',
                                     text=f'{video_files[index]}: {video_info}.')
                    break
                else:
                    bot.send_message(chat_id='1944331333',
                                     text=f'{video_files[index]}: {video_info}. Следующая публикация через {time.strftime("%H:%M:%S", ty_res)}')
                    time.sleep(upload_delay)
        else:
            raise FolderIsEmpty(message=video_folder)
    except Exception as e:
        raise Exception(e)
    else:
        logging.info('All videos published')
        bot.send_message(chat_id='1944331333', text='Все видео опубликованы!')
