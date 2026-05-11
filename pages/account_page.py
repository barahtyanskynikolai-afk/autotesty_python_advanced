import time
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage


class AccountPage(BasePage):

    USERNAME_INPUT = (By.CSS_SELECTOR, "#username")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "#password")
    LOGIN_BTN = (By.CSS_SELECTOR, "button[name='login']")
    REGISTER_BTN = (By.CSS_SELECTOR, "button.custom-register-button")
    LOGOUT_LINK = (
        By.CSS_SELECTOR,
        "nav.woocommerce-MyAccount-navigation a[href*='logout']"
    )
    ACCOUNT_NAV = (By.CSS_SELECTOR, "nav.woocommerce-MyAccount-navigation")
    ERROR_MSG = (By.CSS_SELECTOR, "ul.woocommerce-error li")

    @allure.step("Открыть Мой аккаунт")
    def open_account(self):
        self.open("/my-account/")

    @allure.step("Войти: {username}")
    def login(self, username: str, password: str):
        self.type_text(self.USERNAME_INPUT, username)
        self.type_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BTN)

    @allure.step("Проверить что пользователь залогинен")
    def is_logged_in(self) -> bool:
        if self.is_visible(self.LOGOUT_LINK, timeout=5):
            return True
        if self.is_visible(self.ACCOUNT_NAV, timeout=3):
            return True
        return False

    @allure.step("Нажать Зарегистрироваться")
    def click_register_button(self):
        self.click(self.REGISTER_BTN)

    @allure.step("Выйти из аккаунта")
    def logout(self):
        self.click(self.LOGOUT_LINK)


class RegisterPage(BasePage):

    USERNAME_INPUT = (By.CSS_SELECTOR, "#reg_username")
    EMAIL_INPUT = (By.CSS_SELECTOR, "#reg_email")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "#reg_password")
    REGISTER_BTN = (By.CSS_SELECTOR, "button[name='register']")
    LOGOUT_LINK = (
        By.CSS_SELECTOR,
        "nav.woocommerce-MyAccount-navigation a[href*='logout']"
    )
    ACCOUNT_NAV = (By.CSS_SELECTOR, "nav.woocommerce-MyAccount-navigation")
    ERROR_MSG = (By.CSS_SELECTOR, "ul.woocommerce-error li")

    @allure.step("Открыть страницу регистрации")
    def open_register(self):
        self.open("/register/")

    @allure.step("Зарегистрировать: {username}")
    def register(self, username: str, email: str, password: str):
        self.logger.info(f"Registering: {username} / {email}")
        self.type_text(self.USERNAME_INPUT, username)
        self.type_text(self.EMAIL_INPUT, email)
        self.type_text(self.PASSWORD_INPUT, password)
        self.click(self.REGISTER_BTN)
        import time
        time.sleep(3)
        self.logger.info(f"After register URL: {self.driver.current_url}")

    @allure.step("Пользователь залогинен?")
    def is_registered_and_logged_in(self) -> bool:
        # После регистрации сайт остаётся на /register/ но показывает
        # "Привет username!" в шапке и кнопку "Выйти"
        LOGOUT_HEADER = (By.CSS_SELECTOR, "a[href*='logout']")
        GREETING = (By.CSS_SELECTOR, ".login-woocommerce")

        if self.is_visible(LOGOUT_HEADER, timeout=5):
            self.logger.info("Logged in: logout link found")
            return True
        # Проверяем текст шапки — там появляется "Выйти" вместо "Войти"
        try:
            el = self.driver.find_element(By.CSS_SELECTOR, ".login-woocommerce a")
            text = el.text.strip()
            self.logger.info(f"Header link text: {text!r}")
            if "выйти" in text.lower() or "logout" in text.lower():
                return True
        except Exception:
            pass
        return False

    @allure.step("Получить ошибку регистрации")
    def get_error_message(self) -> str:
        try:
            return self.get_text(self.ERROR_MSG)
        except Exception:
            return ""