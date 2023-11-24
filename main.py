import asyncio
import logging
import os
import random
import traceback
from typing import List, Tuple

import psutil
import telebot  # type: ignore
from requests.exceptions import ConnectionError
import undetected_chromedriver as uc  # type: ignore
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth  # type: ignore
from urllib3.exceptions import MaxRetryError  # type: ignore
from webdriver_manager.chrome import ChromeDriverManager

from parser_account.parser import info_videos, html_code
from upload_video.login import login
from upload_video.post_video import posting_video

logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO)

bot_token = '6670999008:AAF45ZfcAUmu7MbyujGrbJjgLfoJe1FHit0'
bot = telebot.TeleBot(token=bot_token)
unauthorized_accounts = []


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
    options = Options()
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
        logging.info("Internet connection is down!")
        await asyncio.sleep(30)
    else:
        driver.maximize_window()
        stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win64",
                webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)
        driver.get("https://www.tiktok.com/login/phone-or-email/email")
        try:
            logging.info("Browser open")
            session_id = await login(driver=driver, username=username, password=password)
        except ValueError as e:
            logging.error(f"{username}: {e}")
            # bot.send_message(chat_id="641487267", text=f"{number_pc}. {username}: {e}")
        except TypeError as e:
            logging.error(f"{username}: {e}")
            unauthorized_accounts.append((username, password))
        except Exception as e:
            logging.error(e)
        else:
            return session_id
        finally:
            await kill_all_chrome_processes()


async def process_video(number1: int, number2: int, number_pc: int, count_video: int) -> None:
    lines = read_account_file()
    for line in lines:
        await asyncio.sleep(2)
        try:
            username, password = line.split(';')
        except ValueError:
            logging.error(f"#{number_pc}. Line does not match the template: {line}")
        else:
            username, password = username.strip(), password.strip()
            session_id = await start_chrome(username=username, password=password, number_pc=number_pc)
            sleep_time = random.randint(number1, number2) * 60
            try:
                await post_video_and_sleep(session_id, bot, sleep_time, username, number_pc, count_video)

            except Exception as e:
                logging.error(e)

            finally:
                await kill_all_chrome_processes()


async def non_auth_account(number1: int, number2: int, number_pc: int, count_video: int,
                           unauthorized_account: List[Tuple[str, str]]) -> None:
    un_acc = []
    for _ in range(len(unauthorized_account)):
        await asyncio.sleep(2)
        username, password = unauthorized_account.pop()
        un_acc.append((username, password))
        session_id = await start_chrome(username=username, password=password, number_pc=number_pc)
        un_acc.pop()
        sleep_time = random.randint(number1, number2) * 60
        try:
            await post_video_and_sleep(session_id, bot, sleep_time, username, number_pc, count_video)
        except Exception as e:
            logging.error(e)
        finally:
            await kill_all_chrome_processes()
    write_unauthorized_accounts(un_acc)


async def get_video_process(number1: int, number2: int, number_pc: int, count_video: int) -> None:
    print("Launching video uploader")
    await process_video(number1, number2, number_pc, count_video)
    if unauthorized_accounts:
        logging.info(f"#{number_pc}. Unauthorized accounts: {unauthorized_accounts}")
        await non_auth_account(number1, number2, number_pc, count_video, unauthorized_accounts)
    logging.info(f"#{number_pc}. Upload completed!")


async def start_script():
    script = int(input("Enter:\n1 to start video parser\n2 to start video uploader: \n"))
    if script == 1:
        number = int(input("Enter the number of videos to parse: "))
        list_result = await info_videos(number)
        html_code(list_result=list_result)
    elif script == 2:
        number_pc = int(input("Enter the PC number: "))
        count_video = int(input("Number of reposts: "))
        print("Enter the time range for publication (in minutes)")
        number1 = int(input("From (in minutes): "))
        number2 = int(input("To (in minutes): "))
        try:
            await get_video_process(number1, number2, number_pc, count_video)
        except Exception as e:
            logging.error(e)
            logging.error(f"Traceback: {traceback.format_exc()}")
            input("Press Enter to exit")
    else:
        print("Input error!")
        return


def read_account_file() -> List[str]:
    with open("upload_video/accounts.txt", "r", encoding="utf-8") as file:
        lines = file.read().strip().splitlines()
    return lines


def write_unauthorized_accounts(accounts: List[Tuple[str, str]]) -> None:
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
