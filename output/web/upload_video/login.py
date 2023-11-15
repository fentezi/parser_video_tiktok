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
from typing import Any

logging.basicConfig(filename="login.app", filemode="w+", level=logging.INFO, encoding="utf-8")


async def random_sleep():
    sleep_time = random.uniform(0.1, 1.0)
    await asyncio.sleep(sleep_time)


async def solve_captcha_async(multipart_form_data: dict) -> Any:
    url = "https://captcha.ocasoft.com/api/res.php"
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, data=multipart_form_data) as response:
            data = await response.json(content_type='text/html')
            logging.info(data)
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


async def find_captcha(driver, i=0):
    await asyncio.sleep(5)
    try:
        while driver.find_element(By.XPATH, '//*[@id="captcha_container"]/div').is_displayed():
            await asyncio.sleep(3)
            if i != 10:
                if driver.find_element(By.XPATH,
                                       '//*[@id="captcha_container"]/div/div[1]/div[2]/div').text == "Drag the slider to fit the puzzle":
                    full_img_captcha = driver.find_element(By.XPATH,
                                                           '//*[@id="captcha_container"]/div/div[2]/img[1]').get_attribute(
                        'src')
                    small_img_captcha = driver.find_element(By.XPATH,
                                                            '//*[@id="captcha_container"]/div/div[2]/img[2]').get_attribute(
                        'src')
                    action_type = 'tiktokcircle'
                elif driver.find_element(By.XPATH,
                                         '//*[@id="captcha_container"]/div/div[1]/div[2]/div') == "Verify to continue:":
                    full_img_captcha = driver.find_element(By.XPATH,
                                                           '//*[@id="captcha-verify-image"]').get_attribute('src')
                    small_img_captcha = driver.find_element(By.XPATH,
                                                            '//*[@id="captcha_container"]/div/div[2]/img[2]').get_attribute(
                        'src')
                    action_type = 'tiktokpuzzle'
                else:
                    raise TypeError("Another captcha")
            else:
                raise TypeError("No more attempts left")

            user_api_key = '532RJWjTxCmbPMgK74kNLAM5mhJptFtRIrVpDN'
            multipart_form_data = {
                'FULL_IMG_CAPTCHA': (None, full_img_captcha),
                'SMALL_IMG_CAPTCHA': (None, small_img_captcha),
                'ACTION': (None, action_type),
                'USER_KEY': (None, user_api_key)
            }
            data = await solve_captcha_async(multipart_form_data)
            await slide_button(data=data, driver=driver)
        else:
            logging.info("Captcha is not displayed")

    except json.JSONDecodeError:
        driver.find_element(By.XPATH, '//*[@id="captcha_container"]/div/div[4]/div/a[1]').click()
        await find_captcha(driver, i + 1)
    except NoSuchElementException:
        pass


async def login(driver, username: str, password: str, i: int = 0) -> str:
    username_xpath = "//input[@placeholder='Email or username']"
    password_xpath = "//input[@placeholder='Password']"
    submit_button_xpath = "//button[@type='submit']"
    click_go_email = "/html/body/div[1]/div/div[3]/div[1]/div/div[1]/div/div[1]/button[3]"

    await asyncio.sleep(3)
    try:
        text_email = driver.find_element("xpath", click_go_email).text
        if text_email == "Email / Username":
            driver.find_element("xpath", click_go_email).click()
        else:
            driver.find_element("xpath",
                                "/html/body/div[7]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/button[2]").click()

    except NoSuchElementException:
        pass
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

    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located(
            (By.XPATH, submit_button_xpath)))
    except NoSuchElementException as e:
        raise TypeError(e)

    submit_button = driver.find_element("xpath", submit_button_xpath)
    submit_button.click()

    logging.info("Button clicked!")

    await find_captcha(driver)

    await asyncio.sleep(5)
    try:
        error = driver.find_element("xpath",
                                    '//*[@id="loginContainer"]/div[1]/form/div[3]/span').text
        if error == "Maximum number of attempts reached. Try again later.":
            submit_button = driver.find_element("xpath", submit_button_xpath)
            submit_button.click()

            logging.info("Button clicked!")

            await find_captcha(driver)

            await asyncio.sleep(5)
            try:
                session_id = driver.get_cookie("sessionid").get("value")
                logging.info(f"You are logged in: {session_id}")
                return session_id
            except Exception as e:
                raise ValueError(error)
        else:
            raise ValueError(error)
    except NoSuchElementException:
        try:
            session_id = driver.get_cookie("sessionid").get("value")
            logging.info(f"You are logged in: {session_id}")
            return session_id
        except Exception as e:
            raise TypeError(e)
