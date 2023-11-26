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

from parser_account.parser import info_videos, html_code
from upload_video.login import login
from upload_video.post_video import posting_video

logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO)

bot = telebot.TeleBot(
    token='6670999008:AAF45ZfcAUmu7MbyujGrbJjgLfoJe1FHit0')


async def kill_all_chrome_processes() -> None:
    chrome_procs = [proc for proc in psutil.process_iter(['pid', 'name']) if
                    'chrome.exe' in proc.name()]

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


unauthorized_accounts = set()
successful_accounts = set()


def open_file_accounts() -> list:
    with open("upload_video/accounts.txt", "r", encoding="utf-8") as file:
        lines = file.read().strip().splitlines()
    return lines


async def process_video(number1: int, number2: int, number_pc: int, count_video: int) -> None:
    lines = open_file_accounts()

    for line in lines:
        try:
            username, password = line.split(';')
        except ValueError:
            logging.error(f"#{number_pc}. Данная строка не соответствует шаблону: {line}")
            bot.send_message(chat_id="1944331333",
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
                driver = uc.Chrome(options=options, headless=False,
                                   executable_path=ChromeDriverManager().install())
            except (MaxRetryError, ConnectionError):
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
                                             username=username,
                                             password=password)
                except ValueError as e:
                    logging.error(f"#{number_pc}. {username}: {e}")
                    bot.send_message(chat_id="1944331333", text=f"{number_pc}. {username}: {e}")
                except TypeError as e:
                    logging.error(f"#{number_pc}. {username}: {e}")
                    unauthorized_accounts.add((username, password))

                else:
                    logging.info(f"#{number_pc}. Пользователь {username} авторизован!")
                    bot.send_message(chat_id="1944331333",
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
                    except Exception as e:
                        logging.error(e)
        finally:
            await kill_all_chrome_processes()


async def login_unauthorized_accounts(unauthorized_accounts: set[tuple[str, str]], number_pc: int,
                                      number1: int, number2: int, count_video: int) -> None:
    for username, password in unauthorized_accounts:
        options = uc.ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-application-cache")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--mute-audio")
        try:
            driver = uc.Chrome(options=options, headless=False,
                               executable_path=ChromeDriverManager().install())
        except (MaxRetryError, ConnectionError):
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
                                         username=username,
                                         password=password)
            except ValueError as e:
                logging.error(f"#{number_pc}. {username}: {e}")
                bot.send_message(chat_id="1944331333", text=f"{number_pc}. {username}: {e}")

            except TypeError as e:
                logging.error(f"#{number_pc}. {username}: {e}")

            else:
                successful_accounts.add((username, password))
                bot.send_message(chat_id="1944331333",
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
                except Exception as e:
                    logging.error(e)
        finally:
            await kill_all_chrome_processes()

async def get_video_process(number1: int, number2: int, number_pc: int, count_video: int) -> None:
    print("Запуск загрузчика видео")
    await process_video(number1, number2, number_pc, count_video)
    if unauthorized_accounts:
        await login_unauthorized_accounts(unauthorized_accounts, number_pc, number1, number2, count_video)
        with open("upload_video/unauthorized_accounts.txt", "w", encoding="utf-8") as file:
            if not successful_accounts:
                for username, password in unauthorized_accounts:
                    file.write(f"{username};{password}\n")
            else:
                unauthorized_accounts.symmetric_difference_update(successful_accounts)
                for username, password in unauthorized_accounts:
                    file.write(f"{username};{password}\n")


async def start_script():
    script = int(input("Введите:\n1 для запуска парсера видео\n2 для запуска загрузчика видео: \n"))
    if script == 1:
        number = int(input("Введите количество видео для парсинга: "))
        list_result = await info_videos(number)
        await html_code(list_result=list_result)
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
