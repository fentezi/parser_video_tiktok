import random
import time
import json
import requests
import logging
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logging.basicConfig(filename="login.app", filemode="w+", level=logging.INFO)


def random_sleep():
    sleep_time = random.uniform(0.1, 2.0)
    time.sleep(sleep_time)


def find_captcha(driver):
    try:
        time.sleep(5)
        while driver.find_element(By.XPATH,
                                  '//*[@id="captcha_container"]/div').is_displayed() == True:
            time.sleep(3)
            full_img_captcha = driver.find_element("xpath",
                                                   '//*[@id="captcha_container"]/div/div[2]/img[1]').get_attribute(
                'src')
            small_img_captcha = driver.find_element("xpath",
                                                    '//*[@id="captcha_container"]/div/div[2]/img[2]').get_attribute(
                'src')
            action_type = "tiktokcircle"
            user_api_key = "532RJWjTxCmbPMgK74kNLAM5mhJptFtRIrVpDN"

            multipart_form_data = {
                'FULL_IMG_CAPTCHA': (None, full_img_captcha),
                'SMALL_IMG_CAPTCHA': (None, small_img_captcha),
                'ACTION': (None, action_type),
                'USER_KEY': (None, user_api_key)
            }
            solve_captcha = requests.post('https://captcha.ocasoft.com/api/res.php', files=multipart_form_data)
            captcha = driver.find_element("xpath",
                                          '//*[@id="secsdk-captcha-drag-wrapper"]/div[2]')
            data = {}
            if solve_captcha.content:
                data = json.loads(solve_captcha.content)
            number = int(data.get("cordinate_x"))
            actions = ActionChains(driver)
            time.sleep(0.1)
            actions.move_to_element(captcha).perform()
            actions.click_and_hold(captcha).perform()
            for _ in range(number):
                time.sleep(0.001)
                actions.move_by_offset(xoffset=1, yoffset=0).perform()
            actions.release().perform()

            time.sleep(3)

    except NoSuchElementException:
        pass


def login(driver, username: str, password: str):
    login_url = "https://www.tiktok.com/login/phone-or-email/email"
    username_xpath = "//input[@placeholder='Email or username']"
    password_xpath = "//input[@placeholder='Password']"
    submit_button_xpath = "//button[@type='submit']"
    click_go_email = '/html/body/div[1]/div/div[3]/div[1]/div/div[1]/div/div[1]/button[3]'

    driver.get(login_url)
    time.sleep(3)
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
        random_sleep()

    for char in password:
        password_field.send_keys(char)
        random_sleep()

    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located(
            (By.XPATH, submit_button_xpath)))
    except NoSuchElementException as e:
        raise ValueError(e)

    submit_button = driver.find_element("xpath", submit_button_xpath)
    submit_button.click()
    logging.info("Button clicked!")
    time.sleep(3)

    find_captcha(driver)

    time.sleep(3)

    try:
        error = driver.find_element('xpath',
                                    '//*[@id="loginContainer"]/div[1]/form/div[3]/span').text
        logging.error("Authorisation Error: ", error)
        raise Exception(error)
    except NoSuchElementException:
        session_id = driver.get_cookie('sessionid').get('value')
        logging.info(f"You are logged in: {session_id}")

        return session_id
