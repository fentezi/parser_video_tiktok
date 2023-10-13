import logging
import os
import typing

import telebot
import undetected_chromedriver as uc
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


@app.get('/upload_video', response_class=HTMLResponse)
async def upload_video(request: Request):
    return templates.TemplateResponse('video.html', {'request': request})


@app.post('/upload_process', response_class=JSONResponse)
async def upload_process(request: Request, username: str = Form(),
                         password: str = Form()):
    # Настройка Chrome
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = uc.Chrome(use_subprocess=True, headless=False)

    # Настройка stealth
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win64",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)
    try:
        session_id = login(driver, username, password)
    except Exception as e:
        bot.send_message(chat_id='1944331333', text=f'Ошибка: {e}')
        logging.error('Error: {}'.format(str(e)))
    else:
        posting_video(session_id, bot)
    finally:
        driver.quit()
        bot.stop_polling()


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
    uvicorn.run(app)
