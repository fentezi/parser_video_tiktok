import asyncio
import json
import logging
import random
from typing import Any

import aiohttp
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from urllib3.exceptions import ReadTimeoutError, TimeoutError

logging.basicConfig(filename="login.app", filemode="w+", level=logging.INFO, encoding="utf-8")


async def random_sleep():
    sleep_time = random.uniform(0.1, 1.0)
    await asyncio.sleep(sleep_time)


async def solve_captcha_async(multipart_form_data: dict) -> Any:
    url = "https://captcha.ocasoft.com/api/res.php"
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, data=multipart_form_data) as response:
            data = await response.json(content_type='text/html')
            return data


async def slide_button(data: Any, driver):
    captcha = driver.find_element("xpath",
                                  '//*[@id="secsdk-captcha-drag-wrapper"]/div[2]')
    number = int(data.get("cordinate_x"))
    actions = ActionChains(driver)
    await asyncio.sleep(1)
    actions.click_and_hold(captcha).perform()
    actions.move_by_offset(xoffset=number - 5, yoffset=0).perform()
    for _ in range(5):
        actions.move_by_offset(xoffset=1, yoffset=0).perform()
    actions.release().perform()


async def find_captcha(driver, i=8):
    await asyncio.sleep(5)
    try:
        if i != 0:
            if driver.find_element(By.XPATH,
                                   '//*[@id="captcha_container"]/div/div[1]/div[2]/div').text == "Drag the slider to fit the puzzle":
                full_img_captcha = driver.find_element(By.XPATH,
                                                       '//*[@id="captcha_container"]/div/div[2]/img[1]').get_attribute(
                    'src')
                small_img_captcha = driver.find_element(By.XPATH,
                                                        '//*[@id="captcha_container"]/div/div[2]/img[2]').get_attribute(
                    'src')
                action_type = 'tiktokcircle'
        else:
            raise TypeError("Попыток на авторизацию больше нет!")

        user_api_key = 'obgtGU7fmOVfIzDPtUpRFm9v05CVIEG0zNeJAU'
        multipart_form_data = {
            'FULL_IMG_CAPTCHA': (None, full_img_captcha),
            'SMALL_IMG_CAPTCHA': (None, small_img_captcha),
            'ACTION': (None, action_type),
            'USER_KEY': (None, user_api_key)
        }
        data = await solve_captcha_async(multipart_form_data)
        logging.info(f"Информация о капче: {data}")
        await slide_button(data=data, driver=driver)
    except NoSuchElementException:
        raise TypeError("Другой вид капчи!")

    except json.JSONDecodeError:
        driver.find_element(By.XPATH, '//*[@id="captcha_container"]/div/div[4]/div/a[1]').click()
        await find_captcha(driver, i - 1)
    except (ReadTimeoutError, TimeoutError):
        raise TypeError("Отсутствует интернет!")


async def login(driver, username: str, password: str) -> str:
    username_xpath = "//input[@placeholder='Email or username']"
    password_xpath = "//input[@placeholder='Password']"
    submit_button_xpath = "//button[@type='submit']"

    WebDriverWait(driver, 5).until(EC.presence_of_element_located(
        (By.XPATH, username_xpath)))

    username_field = driver.find_element("xpath", username_xpath)
    password_field = driver.find_element("xpath", password_xpath)

    for char in username:
        username_field.send_keys(char)
        await random_sleep()

    for char in password:
        password_field.send_keys(char)
        await random_sleep()

    WebDriverWait(driver, 3).until(EC.presence_of_element_located(
        (By.XPATH, submit_button_xpath)))

    submit_button = driver.find_element("xpath", submit_button_xpath)
    submit_button.click()

    logging.info("Кнопка нажата!")

    try:
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="captcha_container"]/div'))
        )
        await find_captcha(driver)
    except TimeoutException:
        logging.info("Капчи нет!")

    await asyncio.sleep(5)
    try:
        error = driver.find_element("xpath",
                                    '//*[@id="loginContainer"]/div[1]/form/div[3]/span').text

        if error == "Maximum number of attempts reached. Try again later.":
            submit_button = driver.find_element("xpath", submit_button_xpath)
            submit_button.click()
            await asyncio.sleep(3)
            try:
                if driver.find_element(By.XPATH, '//*[@id="captcha_container"]/div').is_displayed():
                    await find_captcha(driver)
            except NoSuchElementException:
                logging.info("Капчи нет!")
        else:
            raise ValueError(error)

        await asyncio.sleep(5)
        try:
            session_id = driver.get_cookie("sessionid").get("value")
            logging.info(f"You are logged in: {session_id}")
            return session_id
        except Exception:
            raise TypeError(error)

    except NoSuchElementException:
        try:
            session_id = driver.get_cookie("sessionid").get("value")
            logging.info(f"You are logged in: {session_id}")
            return session_id
        except Exception as e:
            raise TypeError(e)
