import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage


class MainPage(BasePage):

    FIRST_PIZZA_IMG_LINK = (
        By.CSS_SELECTOR,
        "#product1 li.slick-slide:not(.slick-cloned) .item-img > a:first-child"
    )
    PIZZA_ITEMS = (
        By.CSS_SELECTOR,
        "#product1 li.slick-slide:not(.slick-cloned)"
    )
    FIRST_DESERT_ADD_BTN = (
        By.CSS_SELECTOR,
        "#product2 li.slick-slide:not(.slick-cloned) .add_to_cart_button"
    )

    MENU_PARENT_LINK = (By.CSS_SELECTOR, "#menu-item-389 > a")
    DESSERTS_SUBMENU_LINK = (By.CSS_SELECTOR, "#menu-item-391 > a")
    CART_HEADER_LINK = (By.CSS_SELECTOR, "a.cart-contents")
    ACCOUNT_NAV_LINK = (By.CSS_SELECTOR, "#menu-item-30 > a")

    # Прямая ссылка на товар для добавления через ?add-to-cart=
    PIZZA_4V1_ADD_URL = (
        "http://pizzeria.skillbox.cc/"
        "?add-to-cart=425&quantity=1"
    )

    @allure.step("Открыть главную страницу")
    def open_main(self):
        self.open("/")

    @allure.step("Добавить первую пиццу в корзину")
    def add_first_pizza_to_cart(self):
        """
        Слайдер Slick создаёт клоны которые перекрывают реальные кнопки.
        Добавляем товар через WooCommerce AJAX-ссылку напрямую.
        """
        self.logger.info("Adding pizza via direct add-to-cart URL")
        self.driver.get(self.PIZZA_4V1_ADD_URL)
        # Ждём редиректа обратно на главную или корзину
        WebDriverWait(self.driver, 10).until(
            lambda d: "add-to-cart" not in d.current_url
            or "woocommerce-cart" in d.page_source
        )

    @allure.step("Добавить первый десерт в корзину")
    def add_first_desert_to_cart(self):
        self.logger.info("Adding first desert to cart")
        self.click(self.FIRST_DESERT_ADD_BTN)

    @allure.step("Кликнуть на картинку первой пиццы")
    def click_first_pizza_image(self):
        self.logger.info("Clicking first pizza image")
        self.click(self.FIRST_PIZZA_IMG_LINK)

    @allure.step("Получить количество пицц в слайдере")
    def get_pizza_count(self) -> int:
        items = self.driver.find_elements(*self.PIZZA_ITEMS)
        self.logger.info(f"Pizza count: {len(items)}")
        return len(items)

    @allure.step("Перейти Меню -> Десерты")
    def go_to_desserts_via_menu(self):
        self.hover(self.MENU_PARENT_LINK)
        self.click(self.DESSERTS_SUBMENU_LINK)

    @allure.step("Перейти в корзину")
    def go_to_cart(self):
        self.click(self.CART_HEADER_LINK)

    @allure.step("Перейти в Мой аккаунт")
    def go_to_account(self):
        self.click(self.ACCOUNT_NAV_LINK)