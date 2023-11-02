import asyncio
import logging
import os
import random
import typing

import telebot
import uvicorn
from fastapi import FastAPI, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from selenium import webdriver
from selenium_stealth import stealth

import main
from upload_video.login import login
from upload_video.post_video import posting_video

logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO)

templates = Jinja2Templates(directory='templates')
app = FastAPI()

bot = telebot.TeleBot(
    token='6670999008:AAF45ZfcAUmu7MbyujGrbJjgLfoJe1FHit0')


@app.get('/', response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse('home.html', {'request': request})


@app.get('/parser', response_class=HTMLResponse, name='parser_video')
async def parser_video(request: Request):
    return templates.TemplateResponse('parser.html', {'request': request})


@app.get('/upload_video', response_class=JSONResponse)
async def upload_process(request: Request):
    return templates.TemplateResponse('upload_video.html', {'request': request})


async def process_video():
    with open("accounts.txt", "r", encoding="utf-8") as file:
        lines = file.read().splitlines()
    session_ids = dict()
    drivers = []
    while len(session_ids) != len(lines):
        for line in lines:
            username, password = line.strip().split(';')
            if username not in session_ids.keys():
                options = webdriver.ChromeOptions()
                options.add_argument("--no-sandbox")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                options.add_experimental_option("detach", True)
                options.add_argument("--headless")
                driver = webdriver.Chrome(options=options)
                stealth(driver,
                        languages=["en-US", "en"],
                        vendor="Google Inc.",
                        platform="Win64",
                        webgl_vendor="Intel Inc.",
                        renderer="Intel Iris OpenGL Engine",
                        fix_hairline=True)
                driver.get("https://www.tiktok.com/login/phone-or-email/email")
                try:
                    logging.info("Браузер открыт")
                    session_id = await login(driver=driver,
                                             username=username,
                                             password=password)
                except TypeError as e:
                    logging.error(e)
                    driver.quit()
                except ValueError as e:
                    logging.error(e)
                    bot.send_message(chat_id="1944331333",
                                     text=f"{username}: {e}")
                    driver.quit()

                else:
                    session_ids[username] = session_id
                    drivers.append(driver)
                    bot.send_message(chat_id="1944331333",
                                     text=f"Пользователь {username} авторизован!")
    return session_ids, drivers


stop_tasks = None


@app.post("/video_process")
async def get_video_process(request: Request, number1: int = Form(),
                            number2: int = Form()):
    global stop_tasks
    stop_tasks = False
    session_ids, drivers = await process_video()
    while not stop_tasks:
        if len(os.listdir('video')) == 0:
            bot.send_message(chat_id='1944331333', text='Папка с видео пустая.')
            break
        else:
            for id in session_ids.values():
                sleep_time = random.uniform(number1 * 60, number2 * 60)
                if stop_tasks:
                    bot.send_message(chat_id='1944331333',
                                     text='Загрузка остановлена')
                    break
                elif len(os.listdir('video')) == 1:
                    await posting_video(session_id=id,
                                        bot=bot,
                                        sleep_time=0)
                    break
                else:
                    await posting_video(session_id=id,
                                        bot=bot,
                                        sleep_time=sleep_time)
                    await asyncio.sleep(sleep_time)

    for driver in drivers:
        await asyncio.sleep(1)
        driver.quit()

    return {"message": "upload successful"}


@app.get("/stop_video_processing")
async def stop_video_processing_endpoint():
    global stop_tasks
    stop_tasks = True

    return RedirectResponse("/upload_video")


async def process_uploaded_file(file: UploadFile,
                                number: int) \
        -> typing.List[typing.Tuple[str, str, int, str]]:
    """Process the uploaded file and return the results."""
    # Define a temporary directory where you want to store the uploaded files
    temp_directory = "temp_uploads"
    os.makedirs(temp_directory, exist_ok=True)

    # Generate a unique file name for the uploaded file
    file_name = os.path.join(temp_directory, file.filename).encode()

    # Save the uploaded file to the temporary directory
    with open(file_name, "wb") as f:
        f.write(file.file.read())

    try:
        # Process the file using your info_videos function
        list_result = await main.info_videos(file_name.decode('utf-8'), number)
        return list_result
    except Exception as e:
        # Log the exception
        logging.error(f"Error processing uploaded file: {str(e)}")
        return []


@app.post('/parser_result', response_class=HTMLResponse)
async def result(request: Request, file: UploadFile = Form(),
                 number: int = Form()):
    """Process the uploaded file and return the results."""
    try:
        list_result = await process_uploaded_file(file, number)
        return templates.TemplateResponse('result.html', {"request": request, "list_result": list_result})
    except Exception as e:
        # Redirect to an error page and log the error
        logging.error(f"Error in /result endpoint: {str(e)}")
        error_route_url = app.url_path_for('parser_video')
        return RedirectResponse(error_route_url, status_code=302)


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
