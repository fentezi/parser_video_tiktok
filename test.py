from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
import undetected_chromedriver as uc
from selenium_stealth import stealth

PROXY = '54.37.232.162:3128'


# Настройка Chrome
options = webdriver.ChromeOptions()
options.add_argument("--proxy-server=%s" % PROXY)
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

driver.get("https://whatismyipaddress.com/ru/index")