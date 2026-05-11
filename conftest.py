import pytest
import random
from faker import Faker
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import get_logger
from pages.account_page import RegisterPage

logger = get_logger("conftest")
COUPON_VALID = "GIVEMEHALYAVA"
COUPON_INVALID = "DC120"


@pytest.fixture(scope="function")
def driver():
    options = Options()
    # options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(5)
    yield drv
    drv.quit()


@pytest.fixture(scope="function")
def registered_user(driver):

    fake = Faker("ru_RU")
    rand = random.randint(100, 9999) # Увеличили диапазон для уникальности

    username = f"k{rand}"
    email = f"k{rand}@t.ru"
    password = "Password123!"

    reg = RegisterPage(driver)
    reg.open_register()
    reg.register(username, email, password)

    # Ждем, пока сайт осознает, что мы вошли
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Выйти"))
        )
    except:
        # Если не дождались, выводим URL для отладки
        raise AssertionError(f"Не удалось войти. Мы на странице: {driver.current_url}")

    return {"username": username, "email": email, "password": password}


@pytest.fixture(scope="function")
def cart_with_pizza(driver):
    # Открываем страницу товара напрямую — надёжнее слайдера
    driver.get(
        "http://pizzeria.skillbox.cc/product/"
        "%d0%bf%d0%b8%d1%86%d1%86%d0%b0-4-%d0%b2-1/"
    )
    btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button.single_add_to_cart_button")
        )
    )
    btn.click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.woocommerce-message")
        )
    )
    logger.info("Pizza added to cart")
    return driver