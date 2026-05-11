import time
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage

# Реальная структура /bonus/:
#
# <div id="bonus_main">           — основной контейнер (очищается при успехе)
#   <input id="bonus_username">   — поле Имя (name="username")
#   <input id="bonus_phone">      — поле Телефон (type="tel", name="billing_phone")
#   <div id="bonus_content">      — div для сообщений об ошибках
#   <button name="bonus" onclick="loader()"> — кнопка "Оформить карту"
# </div>
#
# Логика JS-валидации (функция loader()):
#   - Пустое имя   → bonus_content = 'Поле "Имя" обязательно для заполнения'
#   - Пустой тел.  → bonus_content = 'Поле "Телефон" обязательно для заполнения'
#   - Неверный тел.→ bonus_content = "Введен неверный формат телефона"
#   - Верный формат: ^[/\+78]+[0-9]{10,10}$
#     → alert("Заявка отправлена...") + через 6 сек. bonus_main меняется на
#       "<h3>Ваша карта оформлена!</h3>..."
#
# ВАЖНО: при успехе сначала появляется alert() — его нужно принять,
#         затем ждать 6 секунд появления h3.


class BonusPage(BasePage):

    NAME_INPUT = (By.CSS_SELECTOR, "#bonus_username")
    PHONE_INPUT = (By.CSS_SELECTOR, "#bonus_phone")
    SUBMIT_BTN = (By.CSS_SELECTOR, "button[name='bonus']")

    # Контейнер с текстом ошибок валидации
    ERROR_CONTENT = (By.CSS_SELECTOR, "#bonus_content")

    # Заголовок успешной активации (появляется через 6 сек внутри #bonus_main)
    SUCCESS_HEADING = (By.CSS_SELECTOR, "#bonus_main h3")

    # Основной контейнер формы
    BONUS_MAIN = (By.CSS_SELECTOR, "#bonus_main")

    @allure.step("Открыть страницу бонусной программы")
    def open_bonus(self):
        self.logger.info("Opening /bonus/")
        self.open("/bonus/")

    @allure.step("Ввести имя: {name}")
    def enter_name(self, name: str):
        self.logger.info(f"Entering name: {name}")
        self.type_text(self.NAME_INPUT, name)

    @allure.step("Ввести телефон: {phone}")
    def enter_phone(self, phone: str):
        self.logger.info(f"Entering phone: {phone}")
        self.type_text(self.PHONE_INPUT, phone)

    @allure.step("Нажать кнопку 'Оформить карту'")
    def submit_form(self):
        """
        Нажимает кнопку и обрабатывает возможный alert.
        При валидных данных JS показывает alert перед анимацией.
        """
        self.logger.info("Clicking Submit (Оформить карту)")
        self.click(self.SUBMIT_BTN)
        # Принять alert если появился (при успешной отправке)
        try:
            WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            self.logger.info(f"Alert text: {alert.text}")
            alert.accept()
        except Exception:
            self.logger.debug("No alert appeared after submit")

    @allure.step("Дождаться успешной активации карты (до 8 сек)")
    def is_success_visible(self, timeout: int = 8) -> bool:
        """
        Ждёт появления <h3>Ваша карта оформлена!</h3> внутри #bonus_main.
        JS анимация занимает ~6 секунд.
        """
        self.logger.info("Waiting for success heading...")
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.SUCCESS_HEADING)
            )
            text = self.driver.find_element(*self.SUCCESS_HEADING).text
            self.logger.info(f"Success heading text: {text}")
            return "оформлена" in text.lower()
        except Exception:
            self.logger.warning("Success heading not found within timeout")
            return False

    @allure.step("Получить текст ошибки из #bonus_content")
    def get_error_text(self) -> str:
        """Возвращает текст из div#bonus_content (ошибки валидации)."""
        try:
            el = self.find(self.ERROR_CONTENT)
            text = el.text.strip()
            self.logger.info(f"Bonus error text: {text!r}")
            return text
        except Exception:
            return ""

    @allure.step("Проверить наличие ошибки валидации")
    def is_validation_error_visible(self) -> bool:
        """
        Ошибка появляется мгновенно в #bonus_content.
        Проверяем что текст непустой.
        """
        error = self.get_error_text()
        return len(error) > 0

    @allure.step("Проверить что поле имени подсвечено красным")
    def is_name_field_invalid(self) -> bool:
        el = self.find(self.NAME_INPUT)
        style = el.get_attribute("style") or ""
        return "red" in style

    @allure.step("Проверить что поле телефона подсвечено красным")
    def is_phone_field_invalid(self) -> bool:
        el = self.find(self.PHONE_INPUT)
        style = el.get_attribute("style") or ""
        return "red" in style