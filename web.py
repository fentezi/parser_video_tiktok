import asyncio
import logging
import os
import random
from webdriver_manager.chrome import ChromeDriverManager
import psutil
import telebot
import undetected_chromedriver as uc
from selenium_stealth import stealth

from upload_video.login import login
from upload_video.post_video import posting_video

logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO)

bot = telebot.TeleBot(
    token='6670999008:AAF45ZfcAUmu7MbyujGrbJjgLfoJe1FHit0')


async def kill_all_chrome_processes():
    chrome_procs = [proc for proc in psutil.process_iter(['pid', 'name']) if 'chrome.exe' in proc.info['name']]

    for proc in chrome_procs:
        try:
            proc.terminate()
        except psutil.AccessDenied:
            print(f"No permission to terminate process {proc.pid}")


async def process_video(number1: int, number2: int, number_pc: int, count_video: int):
    with open("accounts.txt", "r", encoding="utf-8") as file:
        lines = file.read().splitlines()
    while len(os.listdir('video')) != 0:
        for line in lines:
            await asyncio.sleep(2)
            username, password = line.strip().split(';')
            options = uc.ChromeOptions()
            options.add_argument("--incognito")
            options.add_argument("--mute-audio")
            driver = uc.Chrome(options=options, headless=False,
                               executable_path=ChromeDriverManager().install())
            driver.maximize_window()
            stealth(driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
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
            except TypeError as e:
                logging.error(e)
                await kill_all_chrome_processes()

            else:
                bot.send_message(chat_id="1944331333",
                                 text=f"#{number_pc}. Пользователь {username} авторизован!")
                sleep_time = random.randint(number1, number2) * 60
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
    else:
        bot.send_message(chat_id="1944331333", text="Папка с видео пуста")


async def get_video_process(number1: int, number2: int, number_pc: int, count_video: int):
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
        await get_video_process(number1, number2, number_pc, count_video)
    else:
        print("Неверный ввод")
        await start_script()


asyncio.run(start_script())
