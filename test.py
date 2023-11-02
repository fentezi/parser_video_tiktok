import asyncio
import os

import telebot
from selenium import webdriver
from selenium_stealth import stealth
from upload_video.login import login
from upload_video.post_video import posting_video


async def process_video():
    with open("accounts.txt", "r") as file:
        lines = file.read().splitlines()
    session_ids = dict()
    while len(session_ids) != lines:
        for line in lines:
            options = webdriver.ChromeOptions()
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_experimental_option("detach", True)
            driver = webdriver.Chrome(options=options)
            stealth(driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win64",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True)
            username, password = line.strip().split(";")
            if username not in session_ids.keys():
                driver.get("https://www.tiktok.com/login/phone-or-email/email")
                try:
                    session_id = await login(username=username, password=password, driver=driver)
                except ValueError as e:
                    bot.send_message(chat_id='1944331333', text=f"Ошибка: {e}")
                except TypeError:
                    print("Error")
                else:
                    session_ids[username] = session_id
    return session_ids, driver


bot = telebot.TeleBot(
    token='6670999008:AAF45ZfcAUmu7MbyujGrbJjgLfoJe1FHit0')


async def main():
    session_ids, driver = await process_video()
    try:
        while True:
            if len(os.listdir("video")) == 1:
                break
            else:
                for id in session_ids:
                    await posting_video(session_id=id, bot=bot, sleep_time=60)
                    await asyncio.sleep(60)
    except Exception:
        print("Ошибка")
    finally:
        bot.stop_polling()
        for _ in range(len(session_ids)):
            driver.quit()
    print("Video posted successfully")


if __name__ == "__main__":
    asyncio.run(main())
