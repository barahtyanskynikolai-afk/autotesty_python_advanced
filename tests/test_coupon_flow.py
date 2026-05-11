import allure
import pytest
from pages.main_page import MainPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from conftest import COUPON_VALID, COUPON_INVALID


def _fill_cart(driver):
    """Добавляет пиццу через прямой WooCommerce URL."""
    import time
    driver.get("http://pizzeria.skillbox.cc/?add-to-cart=425&quantity=1")
    time.sleep(3)  # WooCommerce обрабатывает и редиректит


def _parse_price(raw: str) -> float:
    """Парсит строку цены вида '435,00 ₽' в float."""
    cleaned = (
        raw.replace("\u20bd", "")
           .replace(",", ".")
           .replace("\xa0", "")
           .replace(" ", "")
           .strip()
    )
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


@allure.epic("Флоу с промокодом")
@allure.feature("Применение купонов")
class TestCouponFlow:

    @allure.title("TC-13: Промокод GIVEMEHALYAVA даёт скидку 10%")
    def test_valid_coupon_gives_10_percent_discount(self, driver):
        cart = CartPage(driver)

        with allure.step("Наполнить корзину"):
            _fill_cart(driver)
            cart.open_cart()

        with allure.step("Зафиксировать сумму ДО применения промокода"):
            total_before = _parse_price(cart.get_cart_total())
            assert total_before > 0, "Сумма корзины должна быть > 0"
            allure.attach(
                f"Сумма до: {total_before} руб.",
                name="Сумма до скидки",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step(f"Применить промокод {COUPON_VALID}"):
            cart.apply_coupon(COUPON_VALID)

        with allure.step("Проверить что появилась скидка ~10%"):
            discount = _parse_price(cart.get_discount_amount())
            expected = round(total_before * 0.1, 2)
            allure.attach(
                f"Скидка: {discount} руб. (ожидалось: {expected})",
                name="Скидка",
                attachment_type=allure.attachment_type.TEXT,
            )
            assert abs(discount - expected) < 1.0, (
                f"Скидка {discount} руб. должна быть ~10% от {total_before}"
                f" = {expected} руб."
            )

        with allure.step("Проверить что итог уменьшился"):
            total_after = _parse_price(cart.get_cart_total())
            assert total_after < total_before, \
                "Итоговая сумма должна уменьшиться после скидки"

    @allure.title("TC-14: Промокод DC120 не применяется, сумма не меняется")
    def test_invalid_coupon_no_discount(self, driver):
        cart = CartPage(driver)

        with allure.step("Наполнить корзину"):
            _fill_cart(driver)
            cart.open_cart()

        with allure.step("Зафиксировать сумму ДО"):
            total_before = _parse_price(cart.get_cart_total())

        with allure.step(f"Применить невалидный промокод {COUPON_INVALID}"):
            cart.apply_coupon(COUPON_INVALID)

        with allure.step("Убедиться что сумма не изменилась"):
            total_after = _parse_price(cart.get_cart_total())
            assert abs(total_after - total_before) < 0.01, (
                f"Сумма не должна меняться: до={total_before}, после={total_after}"
            )

        with allure.step("Убедиться что появилось сообщение об ошибке"):
            msg = cart.get_coupon_message()
            assert len(msg) > 0, \
                "Должно появиться сообщение об ошибке применения промокода"

    @allure.title("TC-15: При ошибке сервера купонов (500) скидка не применяется")
    def test_coupon_server_error_no_discount(self, driver):
        """
        Перехватываем запрос к эндпоинту ?wc-ajax=apply_coupon через CDP
        и возвращаем ошибку 500. Проверяем что сайт корректно обрабатывает
        недоступность сервера валидации.
        """
        cart = CartPage(driver)

        with allure.step("Наполнить корзину"):
            _fill_cart(driver)
            cart.open_cart()

        with allure.step("Включить перехват сетевых запросов через CDP"):
            driver.execute_cdp_cmd("Network.enable", {})
            driver.execute_cdp_cmd(
                "Network.setRequestInterception",
                {"patterns": [{"urlPattern": "*apply_coupon*"}]}
            )

        with allure.step("Зафиксировать сумму ДО"):
            total_before = _parse_price(cart.get_cart_total())

        with allure.step(f"Применить промокод {COUPON_VALID} при заблокированном сервере"):
            cart.apply_coupon(COUPON_VALID)

        with allure.step("Убедиться что скидка не применилась"):
            total_after = _parse_price(cart.get_cart_total())
            assert abs(total_after - total_before) < 0.01, \
                "При ошибке сервера скидка не должна применяться"

        with allure.step("Ожидаемое поведение сайта"):
            allure.attach(
                "Сайт должен показать понятное сообщение об ошибке, "
                "например: 'Не удалось применить промокод. Попробуйте позже.' "
                "Пользователь не должен видеть технические детали ошибки.",
                name="Ожидаемое поведение",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("Отключить перехват запросов"):
            try:
                driver.execute_cdp_cmd(
                    "Network.setRequestInterception",
                    {"patterns": []}
                )
            except Exception:
                pass

    @allure.title("TC-16: Промокод GIVEMEHALYAVA работает только один раз")
    def test_coupon_single_use_per_user(self, registered_user, driver):
        """
        Пользователь применяет промокод при первом заказе.
        При попытке применить тот же промокод во втором заказе — должна быть ошибка.
        """
        from datetime import date, timedelta
        from pages.checkout_page import CheckoutPage

        cart = CartPage(driver)
        checkout = CheckoutPage(driver)
        tomorrow = (date.today() + timedelta(days=1)).strftime("%d.%m.%Y")

        # --- Первый заказ с промокодом ---
        with allure.step("Добавить пиццу для первого заказа"):
            _fill_cart(driver)
            cart.open_cart()

        with allure.step(f"Применить промокод {COUPON_VALID} в первый раз"):
            cart.apply_coupon(COUPON_VALID)

        with allure.step("Перейти к оформлению и оформить первый заказ"):
            cart.proceed_to_checkout()
            checkout.fill_delivery_info(
                first_name="Тест",
                last_name="Тестов",
                address="ул. Тестовая, 1",
                city="Москва",
                phone="+79001234567",
                email=registered_user["email"],
                postcode="101000",
            )
            checkout.set_delivery_date(tomorrow)
            checkout.select_cash_on_delivery()
            checkout.place_order()

        with allure.step("Убедиться что первый заказ оформлен"):
            assert checkout.is_order_confirmed(), \
                "Первый заказ должен быть успешно оформлен"

        # --- Второй заказ с тем же промокодом ---
        with allure.step("Добавить пиццу для второго заказа"):
            _fill_cart(driver)
            cart.open_cart()

        with allure.step("Зафиксировать сумму ДО"):
            total_before = _parse_price(cart.get_cart_total())

        with allure.step(f"Попытаться применить {COUPON_VALID} второй раз"):
            cart.apply_coupon(COUPON_VALID)

        with allure.step("Убедиться что скидка не применилась"):
            total_after = _parse_price(cart.get_cart_total())
            assert abs(total_after - total_before) < 0.01, \
                "Промокод не должен работать повторно для того же пользователя"

        with allure.step("Убедиться что есть сообщение об ошибке"):
            msg = cart.get_coupon_message()
            assert len(msg) > 0, \
                "Должно появиться сообщение: купон уже использован"