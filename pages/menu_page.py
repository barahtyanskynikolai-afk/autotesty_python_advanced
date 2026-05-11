import allure
from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class MenuPage(BasePage):
    PRODUCT_ITEMS = (By.CSS_SELECTOR, "ul.products li.product")
    ALL_PRICES = (
        By.CSS_SELECTOR,
        "ul.products li.product .price .woocommerce-Price-amount.amount"
    )
    FIRST_ADD_TO_CART = (
        By.CSS_SELECTOR,
        "ul.products li.product:first-child a.add_to_cart_button"
    )

    @allure.step("Открыть категорию Десерты")
    def open_desserts(self):
        self.open("/product-category/menu/deserts/")

    @allure.step("Открыть категорию Пицца")
    def open_pizza(self):
        self.open("/product-category/menu/pizza/")

    @allure.step("Получить все цены на странице")
    def get_all_prices(self) -> list:
        elements = self.driver.find_elements(*self.ALL_PRICES)
        prices = []
        for el in elements:
            raw = el.text.replace("₽", "").replace(",", ".").strip()
            try:
                prices.append(float(raw))
            except ValueError:
                pass
        return prices

    @allure.step("Добавить первый товар в корзину")
    def add_first_item_to_cart(self):
        self.click(self.FIRST_ADD_TO_CART)

    @allure.step("Получить количество товаров")
    def get_products_count(self) -> int:
        return len(self.driver.find_elements(*self.PRODUCT_ITEMS))