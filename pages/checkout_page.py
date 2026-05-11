import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage

# Структура /checkout/ — стандартная WooCommerce форма оформления заказа.
# Из JS locale данных в HTML корзины видны точные id полей:
#
# #billing_first_name  — Имя
# #billing_last_name   — Фамилия
# #billing_address_1   — Адрес (улица и номер дома), maxlength=50
# #billing_city        — Город / Населённый пункт, maxlength=20
# #billing_phone       — Телефон
# #billing_email       — Email
# #billing_country     — Страна (select)
# #billing_state       — Область (select, для RU обязательно)
# #billing_postcode    — Почтовый индекс, maxlength=6
#
# Дата доставки — нестандартное поле, возможно отсутствует.
# Оплата: #payment_method_cod — наличными при доставке
# Кнопка подтверждения: #place_order
#
# Страница подтверждения (thank you):
#   h2.woocommerce-order-received (или .entry-title "Заказ получен")
#   .woocommerce-order-overview — блок с деталями заказа
#   .woocommerce-order-overview__total — итоговая сумма
#
# Редирект на логин при неавторизованном оформлении:
#   .woocommerce-info содержит ссылку на логин


class CheckoutPage(BasePage):

    # --- Поля доставки ---
    FIRST_NAME = (By.CSS_SELECTOR, "#billing_first_name")
    LAST_NAME = (By.CSS_SELECTOR, "#billing_last_name")
    ADDRESS = (By.CSS_SELECTOR, "#billing_address_1")
    CITY = (By.CSS_SELECTOR, "#billing_city")
    PHONE = (By.CSS_SELECTOR, "#billing_phone")
    EMAIL = (By.CSS_SELECTOR, "#billing_email")
    POSTCODE = (By.CSS_SELECTOR, "#billing_postcode")

    # Страна — select через Select()
    COUNTRY_SELECT = (By.CSS_SELECTOR, "#billing_country")
    # Область — select2 виджет (WooCommerce заменяет на кастомный)
    STATE_INPUT = (By.CSS_SELECTOR, "#billing_state")

    # --- Дата доставки (нестандартное поле, может отсутствовать) ---
    DELIVERY_DATE = (By.CSS_SELECTOR, "#order_date, input[name*='date'], input[type='date']")

    # --- Оплата ---
    PAYMENT_COD = (By.CSS_SELECTOR, "#payment_method_cod")
    PAYMENT_COD_LABEL = (By.CSS_SELECTOR, "label[for='payment_method_cod']")

    # --- Кнопка подтверждения ---
    PLACE_ORDER_BTN = (By.CSS_SELECTOR, "#place_order")

    # --- Страница подтверждения заказа ---
    ORDER_RECEIVED_TITLE = (
        By.CSS_SELECTOR,
        "h2.woocommerce-order-received, "
        ".entry-title, "
        "p.woocommerce-thankyou-order-received"
    )
    ORDER_OVERVIEW = (By.CSS_SELECTOR, ".woocommerce-order-overview")
    ORDER_TOTAL = (By.CSS_SELECTOR, ".woocommerce-order-overview__total .woocommerce-Price-amount")
    CUSTOMER_DETAILS = (By.CSS_SELECTOR, ".woocommerce-customer-details address")

    # --- Уведомления ---
    # Редирект "войдите или зарегистрируйтесь"
    LOGIN_NOTICE = (By.CSS_SELECTOR, ".woocommerce-info")
    # Ошибки валидации формы
    FORM_ERRORS = (By.CSS_SELECTOR, "ul.woocommerce-error li")

    @allure.step("Открыть страницу оформления заказа")
    def open_checkout(self):
        self.logger.info("Opening /checkout/")
        self.open("/checkout/")

    @allure.step("Заполнить данные доставки")
    def fill_delivery_info(
        self,
        first_name: str,
        last_name: str,
        address: str,
        city: str,
        phone: str,
        email: str,
        postcode: str = "101000",
    ):
        self.logger.info(f"Filling delivery: {first_name} {last_name}, {city}")
        self.type_text(self.FIRST_NAME, first_name)
        self.type_text(self.LAST_NAME, last_name)
        self.type_text(self.ADDRESS, address)
        self.type_text(self.CITY, city)
        self.type_text(self.PHONE, phone)
        self.type_text(self.EMAIL, email)
        # Почтовый индекс — обязательное поле для RU, maxlength=6
        if self.is_visible(self.POSTCODE, timeout=2):
            self.type_text(self.POSTCODE, postcode)

    @allure.step("Выбрать дату доставки: {date_str}")
    def set_delivery_date(self, date_str: str):
        """Заполняет поле даты если оно существует на странице."""
        self.logger.info(f"Setting delivery date: {date_str}")
        try:
            field = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(self.DELIVERY_DATE)
            )
            field.clear()
            field.send_keys(date_str)
        except Exception:
            self.logger.warning("Delivery date field not found — skipping")

    @allure.step("Выбрать оплату при доставке (COD)")
    def select_cash_on_delivery(self):
        self.logger.info("Selecting Cash on Delivery")
        try:
            radio = self.find(self.PAYMENT_COD)
            if not radio.is_selected():
                # Пробуем кликнуть label (WooCommerce иногда скрывает radio)
                self.click(self.PAYMENT_COD_LABEL)
        except Exception:
            # COD может быть единственным методом и уже выбран
            self.logger.warning("COD radio not found, may be pre-selected")

    @allure.step("Нажать 'Оформить заказ'")
    def place_order(self):
        self.logger.info("Clicking Place Order")
        self.click(self.PLACE_ORDER_BTN)
        # Ждём перехода на страницу подтверждения или ошибку
        WebDriverWait(self.driver, 15).until(
            lambda d: (
                "order-received" in d.current_url
                or d.find_elements(By.CSS_SELECTOR, "ul.woocommerce-error")
            )
        )

    @allure.step("Проверить, что открылась страница подтверждения заказа")
    def is_order_confirmed(self) -> bool:
        # Самый надёжный признак — URL содержит order-received
        confirmed = "order-received" in self.driver.current_url
        if not confirmed:
            # Запасной вариант — заголовок
            confirmed = self.is_visible(self.ORDER_RECEIVED_TITLE, timeout=5)
        self.logger.info(f"Order confirmed: {confirmed}")
        return confirmed

    @allure.step("Получить итоговую сумму заказа из страницы подтверждения")
    def get_order_total(self) -> str:
        try:
            return self.get_text(self.ORDER_TOTAL)
        except Exception:
            return ""

    @allure.step("Получить адрес доставки из подтверждения")
    def get_customer_details(self) -> str:
        try:
            return self.get_text(self.CUSTOMER_DETAILS)
        except Exception:
            return ""

    @allure.step("Получить текст ошибок формы")
    def get_form_errors(self) -> str:
        try:
            errors = self.driver.find_elements(*self.FORM_ERRORS)
            return " | ".join(e.text for e in errors)
        except Exception:
            return ""