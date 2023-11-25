import asyncio
import logging
import os
import random
import traceback
from typing import List

import psutil
import telebot  # type: ignore
import undetected_chromedriver as uc  # type: ignore
from requests.exceptions import ConnectionError
from selenium_stealth import stealth  # type: ignore
from urllib3.exceptions import MaxRetryError  # type: ignore
from webdriver_manager.chrome import ChromeDriverManager

from parser_account.parser import info_videos, html_code
from upload_video.login import login
from upload_video.post_video import posting_video

logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO)

bot_token = '6670999008:AAF45ZfcAUmu7MbyujGrbJjgLfoJe1FHit0'
bot = telebot.TeleBot(token=bot_token)
unauthorized_accounts = set()


async def kill_all_chrome_processes() -> None:
    chrome_procs = [proc for proc in psutil.process_iter(['pid', 'name']) if 'chrome.exe' in proc.name()]
    try:
        for proc in chrome_procs:
            try:
                if psutil.pid_exists(proc.pid):
                    proc.terminate()
                else:
                    logging.info(f"Process {proc.pid} no longer exists.")
            except psutil.AccessDenied:
                logging.error(f"No permission to terminate process {proc.pid}")
            except psutil.NoSuchProcess:
                logging.error(f"Process {proc.pid} no longer exists.")
    except Exception as e:
        logging.info(f"An unexpected error occurred: {e}")


async def start_chrome(username: str, password: str, number_pc: int):
    options = uc.ChromeOptions()
    options.add_argument("--incognito")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-application-cache")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--mute-audio")

    try:
        driver = uc.Chrome(options=options, executable_path=ChromeDriverManager().install(),
                           headless=False)
    except (MaxRetryError, ConnectionError):
        await kill_all_chrome_processes()
        logging.info("Интернет-соединение не работает!")
        await asyncio.sleep(30)
    else:
        driver.maximize_window()
        stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win64",
                webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)
        driver.get("https://www.tiktok.com/login/phone-or-email/email")
        try:
            logging.info("Браузер открыт")
            session_id = await login(driver=driver, username=username, password=password)
        except ValueError as e:
            logging.error(f"{username}: {e}")
            bot.send_message(chat_id="641487267", text=f"#{number_pc}. {username}: {e}")
        except TypeError as e:
            logging.error(f"{username}: {e}")
            unauthorized_accounts.add((username, password))
        except Exception as e:
            logging.error(e)
        else:
            bot.send_message(chat_id="641487267", text=f"#{number_pc}. {username}: Авторизация прошла успешно!")
            return session_id
        finally:
            await kill_all_chrome_processes()


async def process_video(number1: int, number2: int, number_pc: int, count_video: int) -> None:
    lines = read_account_file()
    for line in lines:
        if len(os.listdir('video')) == 0:
            bot.send_message(chat_id="641487267", text=f"#{number_pc}. Папка video пуста!")
            logging.info(f"{number_pc}. Видео не найдено!")
            break
        await asyncio.sleep(2)
        try:
            username, password = line.split(';')
        except ValueError:
            logging.error(f"#{number_pc}. Строка не соответствует шаблону: {line}")
            bot.send_message(chat_id="641487267", text=f"#{number_pc}. Строка не соответствует шаблону: {line}")
        else:
            username, password = username.strip(), password.strip()
            session_id = await start_chrome(username=username, password=password, number_pc=number_pc)
            sleep_time = random.randint(number1, number2) * 60
            try:
                await post_video_and_sleep(session_id, bot, sleep_time, username, number_pc, count_video)

            except Exception as e:
                logging.error(e)


succes_acc = set()


async def non_auth_account(number1: int, number2: int, number_pc: int, count_video: int,
                           unauthorized_account: set[tuple[str, str]], succes_acc: set) -> None:
    for username, password in unauthorized_account:
        await asyncio.sleep(2)
        session_id = await start_chrome(username=username, password=password, number_pc=number_pc)
        succes_acc.add((username, password))
        sleep_time = random.randint(number1, number2) * 60
        try:
            await post_video_and_sleep(session_id, bot, sleep_time, username, number_pc, count_video)
        except Exception as e:
            logging.error(e)


async def get_video_process(number1: int, number2: int, number_pc: int, count_video: int) -> None:
    print("Запуск загрузчика видео!")
    if len(os.listdir('video')) == 0:
        logging.info(f"{number_pc}. Видео не найдено!")
        return
    with open("upload_video/unauthorized_accounts.txt", "w", encoding="utf-8") as file:
        file.write("")
    await process_video(number1, number2, number_pc, count_video)
    if unauthorized_accounts:
        await non_auth_account(number1, number2, number_pc, count_video, unauthorized_accounts, succes_acc)
        logging.info(unauthorized_accounts)
        if not succes_acc:
            write_unauthorized_accounts(unauthorized_accounts)
        else:
            unauthorized_accounts.symmetric_difference_update(succes_acc)
            write_unauthorized_accounts(unauthorized_accounts)
        logging.info(f"#{number_pc}. Неавторизованные аккаунты: {unauthorized_accounts}")
    logging.info(f"#{number_pc}. Загрузка завершена!")
    bot.send_message(chat_id="641487267", text=f"#{number_pc}. Загрузка завершена!")


async def start_script():
    script = int(input("Введите:\n1, чтобы запустить анализатор видео\n2, чтобы начать загрузку видео: \n"))
    if script == 1:
        number = int(input("Введите количество видео для анализа:"))
        list_result = await info_videos(number)
        html_code(list_result=list_result)
    elif script == 2:
        number_pc = int(input("Введите номер ПК: "))
        count_video = int(input("Количество репостов: "))
        print("Введите временной диапазон публикации (в минутах)")
        number1 = int(input("От (в минутах): "))
        number2 = int(input("До (в минутах): "))
        try:
            await get_video_process(number1, number2, number_pc, count_video)
        except Exception as e:
            logging.error(e)
            logging.error(f"Traceback: {traceback.format_exc()}")
            input("Нажмите Enter, чтобы выйти")
    else:
        print("Ошибка ввода!")
        return


def read_account_file() -> List[str]:
    with open("upload_video/accounts.txt", "r", encoding="utf-8") as file:
        lines = file.read().strip().splitlines()
    return lines


def write_unauthorized_accounts(accounts: set[tuple[str, str]]) -> None:
    with open("upload_video/unauthorized_accounts.txt", "w", encoding="utf-8") as file:
        for username, password in accounts:
            file.write(f"{username};{password}\n")


async def post_video_and_sleep(session_id: str, bot, sleep_time: int, username: str, number_pc: int,
                               count_video: int) -> None:
    if len(os.listdir('video')) == 1:
        await posting_video(session_id=session_id, bot=bot, sleep_time=0, username=username, number_pc=number_pc,
                            count_publish=count_video)
        return
    else:
        await posting_video(session_id=session_id, bot=bot, sleep_time=sleep_time, username=username,
                            number_pc=number_pc, count_publish=count_video)


if __name__ == '__main__':
    asyncio.run(start_script())
