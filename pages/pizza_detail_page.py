import allure
from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class PizzaDetailPage(BasePage):
    PIZZA_TITLE = (By.CSS_SELECTOR, "h1.product_title.entry-title")
    ADDON_RADIO_BTNS = (By.CSS_SELECTOR, ".wc-pao-addon-container input[type='radio']")
    ADD_TO_CART_BTN = (By.CSS_SELECTOR, "button.single_add_to_cart_button")
    SUCCESS_MSG = (By.CSS_SELECTOR, "div.woocommerce-message")

    @allure.step("Получить название пиццы")
    def get_pizza_title(self) -> str:
        return self.get_text(self.PIZZA_TITLE)

    def get_current_url(self) -> str:
        return self.driver.current_url

    @allure.step("Выбрать дополнительную опцию (индекс={index})")
    def select_addon_option(self, index: int = 0):
        btns = self.driver.find_elements(*self.ADDON_RADIO_BTNS)
        if btns:
            btns[index].click()

    @allure.step("Нажать Добавить в корзину")
    def add_to_cart(self):
        self.click(self.ADD_TO_CART_BTN)

    @allure.step("Проверить сообщение об успешном добавлении")
    def is_success_message_visible(self) -> bool:
        return self.is_visible(self.SUCCESS_MSG)