import asyncio
import logging
import os
import random
import traceback

import psutil
import telebot  # type: ignore
import undetected_chromedriver as uc  # type: ignore
from requests.exceptions import ConnectionError
from selenium_stealth import stealth  # type: ignore
from urllib3.exceptions import MaxRetryError
from webdriver_manager.chrome import ChromeDriverManager

from upload_video.login import login
from upload_video.post_video import posting_video

logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO)

bot = telebot.TeleBot(
    token='6670999008:AAF45ZfcAUmu7MbyujGrbJjgLfoJe1FHit0')


async def kill_all_chrome_processes() -> None:
    chrome_procs = [proc for proc in psutil.process_iter(['pid', 'name']) if 'chrome.exe' in proc.info['name']]

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



async def process_video(number1: int, number2: int, number_pc: int, count_video: int) -> None:
    with open("accounts.txt", "r", encoding="utf-8") as file:
        lines = file.read().strip().splitlines()

    while len(os.listdir('video')) != 0:
        for line in lines:
            await asyncio.sleep(2)
            try:
                username, password = line.split(';')
            except ValueError:
                logging.error(f"#{number_pc}. Данная строка не соответствует шаблону: {line}")
                bot.send_message(chat_id="641487267",
                                 text=f"#{number_pc}. Данная строка не соответствует шаблону: {line}")
            else:
                username = username.strip()
                password = password.strip()
            options = uc.ChromeOptions()
            options.add_argument("--incognito")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-application-cache")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--mute-audio")
            try:
                driver = uc.Chrome(options=options, headless=True,
                                   executable_path=ChromeDriverManager().install())
            except (MaxRetryError, ConnectionError):
                await kill_all_chrome_processes()
                logging.info("Internet connection is down!")
                await asyncio.sleep(30)
            else:
                driver.maximize_window()
                stealth(driver,
                        languages=["en-US", "en"],
                        vendor="Google Inc.",
                        platform="Win64",
                        webgl_vendor="Intel Inc.",
                        renderer="Intel Iris OpenGL Engine",
                        fix_hairline=True,
                        )
                driver.get("https://www.tiktok.com/login/phone-or-email/email")
                try:
                    logging.info("Browser open")
                    session_id = await login(driver=driver,
                                             username=usernam,
                                             password=password)
                except ValueError as e:
                    logging.error(f"{username}: {e}")
                    bot.send_message(chat_id="641487267", text=f"{number_pc}. {username}: {e}")

                except Exception as e:
                    logging.error(e)
                    await kill_all_chrome_processes()

                else:
                    bot.send_message(chat_id="641487267",
                                     text=f"#{number_pc}. Пользователь {username} авторизован!")
                    sleep_time = random.randint(number1, number2) * 60
                    try:
                        if len(os.listdir('video')) == 1:
                            await posting_video(session_id=session_id,
                                                bot=bot,
                                                sleep_time=0,
                                                username=username,
                                                number_pc=number_pc,
                                                count_publish=count_video)
                            break
                        else:
                            await posting_video(session_id=session_id,
                                                bot=bot,
                                                sleep_time=sleep_time,
                                                username=username,
                                                number_pc=number_pc,
                                                count_publish=count_video)
                            await asyncio.sleep(sleep_time)
                        await kill_all_chrome_processes()
                    except Exception as e:
                        logging.error(e)
                        await kill_all_chrome_processes()
    else:
        bot.send_message(chat_id="641487267", text="Папка с видео пуста")
        await kill_all_chrome_processes()


async def get_video_process(number1: int, number2: int, number_pc: int, count_video: int) -> None:
    print("Запуск загрузчика видео")
    await process_video(number1, number2, number_pc, count_video)


async def start_script():
    script = int(input("Введите:\n1 для запуска парсера видео\n2 для запуска загрузчика видео: \n"))
    if script == 1:
        number = int(input("Введите количество видео для парсинга: "))
        # await main.info_videos(number=number)
    elif script == 2:
        number_pc = int(input("Введите номер ПК: "))
        count_video = int(input("Количество повторных публикаций: "))
        print("Введите диапазон времени для публикации (в минутах)")
        number1 = int(input("От (в минутах): "))
        number2 = int(input("До (в минутах): "))
        try:
            await get_video_process(number1, number2, number_pc, count_video)
        except Exception as e:
            logging.error(e)
            logging.error(f"Traceback: {traceback.format_exc()}")
            input("Нажмите Enter для выхода")
    else:
        print("Ошибка ввода!")
        return


if __name__ == "__main__":
    asyncio.run(start_script())
