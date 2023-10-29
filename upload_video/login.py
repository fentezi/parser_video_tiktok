import asyncio
import json
import logging
import random

import aiohttp
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logging.basicConfig(filename="login.app", filemode="w+", level=logging.INFO)


async def random_sleep():
    sleep_time = random.uniform(0.1, 2.0)
    await asyncio.sleep(sleep_time)


async def solve_captcha_async(multipart_form_data: dict):
    url = "https://captcha.ocasoft.com/api/res.php"
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, data=multipart_form_data) as response:
            if response.status == 200:
                data = await response.json(content_type='text/html')
                return data
            else:
                pass


async def slide_button(data, driver):
    captcha = driver.find_element("xpath",
                                  '//*[@id="secsdk-captcha-drag-wrapper"]/div[2]')
    number = int(data.get("cordinate_x"))
    actions = ActionChains(driver)
    await asyncio.sleep(0.1)
    actions.click_and_hold(captcha).perform()
    for _ in range(number):
        actions.move_by_offset(xoffset=1, yoffset=0).perform()
    actions.release().perform()
    await asyncio.sleep(3)


async def find_captcha(driver):
    i = 0
    try:
        while driver.find_element(By.XPATH,
                                  '//*[@id="captcha_container"]/div').is_displayed():
            await asyncio.sleep(1)
            logging.info(i)
            if i > 3 & i < 6:
                full_img_captcha = driver.find_element(By.XPATH,
                                                       '/img').get_attribute(
                    'src')
                small_img_captcha = driver.find_element(By.XPATH,
                                                        '/img').get_attribute(
                    'src')
                action_type = "tiktokpuzzle"

            elif i <= 3:
                full_img_captcha = driver.find_element(By.XPATH,
                                                       '//*[@id="captcha_container"]/div/div[2]/img[1]').get_attribute(
                    'src')
                small_img_captcha = driver.find_element(By.XPATH,
                                                        '//*[@id="captcha_container"]/div/div[2]/img[2]').get_attribute(
                    'src')
                action_type = "tiktokcircle"
            else:
                raise TypeError
            i += 1
            user_api_key = "532RJWjTxCmbPMgK74kNLAM5mhJptFtRIrVpDN"
            multipart_form_data = {
                'FULL_IMG_CAPTCHA': (None, full_img_captcha),
                'SMALL_IMG_CAPTCHA': (None, small_img_captcha),
                'ACTION': (None, action_type),
                'USER_KEY': (None, user_api_key)
            }
            data = await solve_captcha_async(multipart_form_data)
            await slide_button(data=data, driver=driver)
        else:
            logging.info("Captcha solved!")

    except json.JSONDecodeError:
        driver.find_element(By.XPATH,
                            '//*[@id="captcha_container"]/div/div[4]/div/a[1]').click()
        await find_captcha(driver)
    except NoSuchElementException:
        pass


async def login(driver, username: str, password: str):
    login_url = "https://www.tiktok.com/login/phone-or-email/email"
    username_xpath = "//input[@placeholder='Email or username']"
    password_xpath = "//input[@placeholder='Password']"
    submit_button_xpath = "//button[@type='submit']"
    click_go_email = '/html/body/div[1]/div/div[3]/div[1]/div/div[1]/div/div[1]/button[3]'

    driver.get(login_url)
    await asyncio.sleep(3)
    try:
        text_email = driver.find_element("xpath", click_go_email).text
        if text_email == "Email / Username":
            driver.find_element('xpath', click_go_email).click()
        else:
            driver.find_element("xpath",
                                '/html/body/div[7]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/button[2]').click()

    except NoSuchElementException:
        pass
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.XPATH, username_xpath)))

    username_field = driver.find_element("xpath", username_xpath)
    password_field = driver.find_element("xpath", password_xpath)

    for char in username:
        username_field.send_keys(char)
        await random_sleep()

    for char in password:
        password_field.send_keys(char)
        await random_sleep()

    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located(
            (By.XPATH, submit_button_xpath)))
    except NoSuchElementException as e:
        raise TypeError(e)

    try:
        submit_button = driver.find_element("xpath", submit_button_xpath)
        submit_button.click()
    except NoSuchElementException as e:
        raise TypeError(e)
    logging.info("Button clicked!")
    await asyncio.sleep(3)

    await find_captcha(driver)

    await asyncio.sleep(5)

    try:
        error = driver.find_element('xpath',
                                    '//*[@id="loginContainer"]/div[1]/form/div[3]/span').text
        logging.error("Authorisation Error: ", error)
        raise ValueError(error)
    except NoSuchElementException:
        try:
            session_id = driver.get_cookie('sessionid').get('value')
            logging.info(f"You are logged in: {session_id}")
        except Exception as e:
            logging.error(e)
            raise TypeError
        else:
            return session_id
