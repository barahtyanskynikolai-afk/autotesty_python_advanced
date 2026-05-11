import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage

# Структура корзины WooCommerce /cart/ (с товарами):
#
# <table class="shop_table woocommerce-cart-form__contents">
#   <tr class="woocommerce-cart-form__cart-item cart_item">
#     <td class="product-remove">
#       <a class="remove" href="?remove_item=...">×</a>
#     </td>
#     <td class="product-name">
#       <a>Пицца «4 в 1»</a>
#     </td>
#     <td class="product-quantity">
#       <input type="number" class="input-text qty text" name="cart[key][qty]" value="1">
#     </td>
#     <td class="product-subtotal">
#       <span class="woocommerce-Price-amount amount">435,00₽</span>
#     </td>
#   </tr>
# </table>
#
# Итого:
# <div class="cart_totals">
#   <table class="shop_table shop_table_responsive">
#     <tr class="order-total">
#       <td><strong><span class="woocommerce-Price-amount amount">435,00₽</span></strong></td>
#     </tr>
#   </table>
# </div>
#
# Купон:
# <div class="coupon">
#   <input id="coupon_code" name="coupon_code">
#   <button name="apply_coupon">Применить купон</button>
# </div>
#
# Скидка (появляется после применения купона):
# <tr class="cart-discount coupon-GIVEMEHALYAVA">
#   <td><span class="woocommerce-Price-amount amount">-43,50₽</span></td>
# </tr>
#
# Уведомления: div.woocommerce-message / ul.woocommerce-error
# Кнопка обновить: button[name="update_cart"]
# Кнопка оформить: a.checkout-button


class CartPage(BasePage):

    # Строки товаров
    CART_ITEMS = (By.CSS_SELECTOR, "tr.woocommerce-cart-form__cart-item")
    ITEM_NAME = (By.CSS_SELECTOR, "td.product-name a")
    ITEM_QTY_INPUT = (By.CSS_SELECTOR, "td.product-quantity input.qty")
    REMOVE_BTN = (By.CSS_SELECTOR, "td.product-remove a.remove")

    # Кнопки
    UPDATE_CART_BTN = (By.CSS_SELECTOR, "button[name='update_cart']")
    CHECKOUT_BTN = (By.CSS_SELECTOR, "a.checkout-button")

    # Итого
    CART_TOTAL = (By.CSS_SELECTOR, "tr.order-total td .woocommerce-Price-amount.amount")

    # Купон
    COUPON_INPUT = (By.CSS_SELECTOR, "#coupon_code")
    APPLY_COUPON_BTN = (By.CSS_SELECTOR, "button[name='apply_coupon']")

    # Скидка (строка появляется после применения купона)
    DISCOUNT_AMOUNT = (By.CSS_SELECTOR, "tr.cart-discount td .woocommerce-Price-amount.amount")

    # Уведомления
    SUCCESS_MSG = (By.CSS_SELECTOR, ".woocommerce-message")
    ERROR_MSG = (By.CSS_SELECTOR, "ul.woocommerce-error li")
    ANY_NOTICE = (By.CSS_SELECTOR, ".woocommerce-message, ul.woocommerce-error")

    # Пустая корзина
    EMPTY_CART = (By.CSS_SELECTOR, "p.cart-empty")

    @allure.step("Открыть страницу корзины")
    def open_cart(self):
        self.logger.info("Opening /cart/")
        self.open("/cart/")

    @allure.step("Получить количество позиций в корзине")
    def get_items_count(self) -> int:
        try:
            # Ждём недолго — корзина может быть пустой
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(self.CART_ITEMS)
            )
            count = len(self.driver.find_elements(*self.CART_ITEMS))
        except Exception:
            count = 0
        self.logger.info(f"Cart items count: {count}")
        return count

    @allure.step("Изменить количество товара (индекс={index}) на {qty}")
    def set_item_quantity(self, index: int, qty: int):
        self.logger.info(f"Setting item[{index}] qty to {qty}")
        inputs = self.driver.find_elements(*self.ITEM_QTY_INPUT)
        if not inputs:
            raise Exception("Quantity inputs not found in cart")
        inp = inputs[index]
        inp.clear()
        inp.send_keys(str(qty))

    @allure.step("Нажать 'Обновить корзину'")
    def update_cart(self):
        self.logger.info("Clicking Update Cart")
        self.click(self.UPDATE_CART_BTN)
        # Ждём пока страница обновится
        WebDriverWait(self.driver, 10).until(
            EC.staleness_of(self.driver.find_element(*self.UPDATE_CART_BTN))
        ) if self.is_visible(self.UPDATE_CART_BTN, timeout=1) else None

    @allure.step("Удалить товар из корзины (индекс={index})")
    def remove_item(self, index: int = 0):
        self.logger.info(f"Removing cart item[{index}]")
        btns = self.driver.find_elements(*self.REMOVE_BTN)
        if not btns:
            raise Exception("Remove buttons not found")
        btns[index].click()
        # Ждём обновления DOM
        WebDriverWait(self.driver, 5).until(
            EC.staleness_of(btns[index])
        )

    @allure.step("Получить итоговую сумму корзины")
    def get_cart_total(self) -> str:
        # После AJAX-обновления корзины перезапрашиваем элемент
        import time
        time.sleep(1)  # даём WooCommerce обновить DOM
        total = self.get_text(self.CART_TOTAL)
        self.logger.info(f"Cart total: {total!r}")
        return total

    @allure.step("Перейти к оформлению заказа")
    def proceed_to_checkout(self):
        import time
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        self.logger.info("Clicking checkout button")
        # После apply_coupon WooCommerce делает AJAX и перерисовывает корзину.
        # Ждём пока анимация загрузки исчезнет, затем находим кнопку заново.
        time.sleep(2)
        # Находим кнопку заново — старая ссылка невалидна после AJAX
        btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.checkout-button"))
        )
        btn.click()

    @allure.step("Получить сумму скидки")
    def get_discount_amount(self) -> str:
        try:
            discount = self.get_text(self.DISCOUNT_AMOUNT)
            self.logger.info(f"Discount: {discount!r}")
            return discount
        except Exception:
            self.logger.warning("Discount row not found")
            return "0"

    @allure.step("Применить купон: {coupon}")
    def apply_coupon(self, coupon: str):
        self.logger.info(f"Applying coupon: {coupon}")
        self.type_text(self.COUPON_INPUT, coupon)
        self.click(self.APPLY_COUPON_BTN)
        # Ждём появления уведомления
        self.is_visible(self.ANY_NOTICE, timeout=5)

    @allure.step("Получить текст уведомления (успех или ошибка)")
    def get_coupon_message(self) -> str:
        for locator in [self.SUCCESS_MSG, self.ERROR_MSG]:
            if self.is_visible(locator, timeout=2):
                msg = self.get_text(locator)
                self.logger.info(f"Coupon message: {msg!r}")
                return msg
        return ""

    @allure.step("Перейти к оформлению заказа")
    def proceed_to_checkout(self):
        self.logger.info("Clicking checkout button")
        self.click(self.CHECKOUT_BTN)

    @allure.step("Корзина пуста?")
    def is_cart_empty(self) -> bool:
        return self.is_visible(self.EMPTY_CART, timeout=3)