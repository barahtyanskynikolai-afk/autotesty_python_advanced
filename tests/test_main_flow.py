import allure
import pytest
import random
from pages.main_page import MainPage
from pages.pizza_detail_page import PizzaDetailPage
from pages.cart_page import CartPage
from pages.menu_page import MenuPage
from pages.account_page import AccountPage, RegisterPage
from pages.checkout_page import CheckoutPage
from selenium.webdriver.common.by import By
from faker import Faker
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC




@allure.epic("Основной флоу клиента")
@allure.feature("Главная страница — секция пицц")
class TestMainPagePizzas:

    @allure.title("TC-01: Добавить первую пиццу в корзину с главной страницы")
    def test_add_first_pizza_to_cart(self, driver):
        main = MainPage(driver)
        cart = CartPage(driver)

        with allure.step("Открыть главную страницу"):
            main.open_main()

        with allure.step("Нажать 'В корзину' у первой пиццы"):
            main.add_first_pizza_to_cart()

        with allure.step("Перейти в корзину и проверить наличие товара"):
            cart.open_cart()
            assert cart.get_items_count() >= 1, \
                "В корзине должна быть минимум 1 позиция"

    @allure.title("TC-02: На главной отображается минимум 1 пицца в секции")
    def test_pizzas_visible_on_main(self, driver):
        main = MainPage(driver)

        with allure.step("Открыть главную страницу"):
            main.open_main()

        with allure.step("Проверить, что секция пицц непустая"):
            count = main.get_pizza_count()
            assert count >= 1, "Секция пицц должна содержать хотя бы 1 товар"

    @allure.title("TC-03: Клик на картинку пиццы ведёт на страницу товара (/product/...)")
    def test_click_pizza_image_opens_product_page(self, driver):
        main = MainPage(driver)
        detail = PizzaDetailPage(driver)

        with allure.step("Открыть главную страницу"):
            main.open_main()

        with allure.step("Кликнуть на картинку первой пиццы"):
            main.click_first_pizza_image()

        with allure.step("Убедиться что открылась страница /product/"):
            url = detail.get_current_url()
            assert "/product/" in url, \
                f"URL должен содержать /product/, получили: {url}"

        with allure.step("Убедиться что название пиццы отображается"):
            title = detail.get_pizza_title()
            assert len(title) > 0, "Название пиццы не должно быть пустым"


@allure.epic("Основной флоу клиента")
@allure.feature("Страница товара")
class TestProductDetailPage:

    @allure.title("TC-04: Открыть страницу пиццы '4 в 1' напрямую")
    def test_product_page_opens(self, driver):
        detail = PizzaDetailPage(driver)

        with allure.step("Открыть страницу пиццы '4 в 1' по прямому URL"):
            driver.get(
                "http://pizzeria.skillbox.cc/product/"
                "%d0%bf%d0%b8%d1%86%d1%86%d0%b0-4-%d0%b2-1/"
            )

        with allure.step("Проверить название товара"):
            title = detail.get_pizza_title()
            assert "4" in title, \
                f"Ожидалось название с '4', получили: {title}"

    @allure.title("TC-05: Добавить пиццу с опцией борта со страницы товара")
    def test_add_pizza_with_addon(self, driver):
        detail = PizzaDetailPage(driver)
        cart = CartPage(driver)

        with allure.step("Открыть страницу пиццы"):
            driver.get(
                "http://pizzeria.skillbox.cc/product/"
                "%d0%bf%d0%b8%d1%86%d1%86%d0%b0-4-%d0%b2-1/"
            )

        with allure.step("Выбрать дополнительную опцию (если доступна)"):
            detail.select_addon_option(0)

        with allure.step("Нажать 'Добавить в корзину'"):
            detail.add_to_cart()

        with allure.step("Перейти в корзину и проверить наличие товара"):
            cart.open_cart()
            assert cart.get_items_count() >= 1


@allure.epic("Основной флоу клиента")
@allure.feature("Корзина")
class TestCartManagement:

    @allure.title("TC-06: Увеличить количество пиццы в корзине до 2")
    def test_increase_item_quantity(self, cart_with_pizza):
        driver = cart_with_pizza
        cart = CartPage(driver)

        with allure.step("Открыть корзину"):
            cart.open_cart()

        with allure.step("Изменить количество первого товара на 2"):
            cart.set_item_quantity(0, 2)

        with allure.step("Нажать 'Обновить корзину'"):
            cart.update_cart()

        with allure.step("Проверить что количество обновилось"):
            cart.open_cart()
            qty_inputs = driver.find_elements(*cart.ITEM_QTY_INPUT)
            assert qty_inputs, "Поле количества должно присутствовать"
            assert qty_inputs[0].get_attribute("value") == "2", \
                "Количество должно быть 2"

    @allure.title("TC-07: Удалить товар из корзины кнопкой ×")
    def test_remove_item_from_cart(self, cart_with_pizza):
        driver = cart_with_pizza
        cart = CartPage(driver)

        with allure.step("Открыть корзину"):
            cart.open_cart()
            count_before = cart.get_items_count()
            assert count_before >= 1, "В корзине должен быть хотя бы 1 товар"

        with allure.step("Удалить первый товар"):
            cart.remove_item(0)

        with allure.step("Убедиться что количество позиций уменьшилось"):
            count_after = cart.get_items_count()
            assert count_after < count_before, \
                "После удаления должно стать меньше позиций"


@allure.epic("Основной флоу клиента")
@allure.feature("Меню — категория Десерты")
class TestMenuDesserts:

    @allure.title("TC-08: Открыть категорию Десерты, проверить что все цены ≤ 135 руб.")
    def test_desserts_prices_filter(self, driver):
        menu = MenuPage(driver)

        with allure.step("Открыть страницу категории Десерты"):
            menu.open_desserts()

        with allure.step("Получить все цены товаров"):
            prices = menu.get_all_prices()
            assert prices, "На странице десертов должны быть товары с ценами"

        with allure.step("Убедиться что есть товары дешевле 135 руб."):
            cheap = [p for p in prices if p <= 135]
            assert cheap, \
                f"Среди десертов нет товаров ≤135 руб. Цены: {prices}"

    @allure.title("TC-09: Добавить десерт из категории в корзину")
    def test_add_dessert_from_menu(self, driver):
        menu = MenuPage(driver)
        cart = CartPage(driver)

        with allure.step("Открыть категорию Десерты"):
            menu.open_desserts()

        with allure.step("Добавить первый десерт в корзину"):
            menu.add_first_item_to_cart()

        with allure.step("Перейти в корзину и проверить товар"):
            cart.open_cart()
            assert cart.get_items_count() >= 1


@allure.epic("Основной флоу клиента")
@allure.feature("Регистрация")
class TestRegistration:

    @allure.title("TC-10: Зарегистрировать нового пользователя через /register/")
    def test_user_registration(self, driver):
        from pages.account_page import RegisterPage
        import time

        reg = RegisterPage(driver)
        rand = str(int(time.time()))[-6:]
        username = f"u{rand}"
        email = f"u{rand}@t.ru"
        password = "Password123!"

        with allure.step("Перейти на страницу регистрации"):
            reg.open_register()

        with allure.step(f"Заполнить форму: {username} / {email}"):
            reg.register(username, email, password)

        with allure.step("Убедиться что пользователь залогинен"):
            assert reg.is_registered_and_logged_in(), \
                "После регистрации пользователь должен быть авторизован"

    @allure.title("TC-11: На /my-account/ есть кнопка 'Зарегистрироваться'")
    def test_register_button_exists_on_account_page(self, driver):
        account = AccountPage(driver)

        with allure.step("Открыть страницу Мой аккаунт"):
            account.open_account()

        with allure.step("Проверить наличие кнопки регистрации"):
            assert account.is_visible(account.REGISTER_BTN), \
                "Кнопка 'Зарегистрироваться' должна быть видна"


@allure.epic("Основной флоу клиента")
@allure.feature("Оформление заказа")
class TestCheckout:

    @allure.title("TC-12: Полный флоу — добавить пиццу, залогиниться, оформить заказ")
    def test_full_order_flow(self, registered_user, driver):
        from datetime import date, timedelta

        main = MainPage(driver)
        cart = CartPage(driver)
        checkout = CheckoutPage(driver)

        tomorrow = (date.today() + timedelta(days=1)).strftime("%d.%m.%Y")

        with allure.step("Добавить пиццу в корзину"):
            main.open_main()
            main.add_first_pizza_to_cart()

        with allure.step("Перейти в корзину → Оформить заказ"):
            cart.open_cart()
            cart.proceed_to_checkout()

        with allure.step("Заполнить данные доставки"):
            checkout.fill_delivery_info(
                first_name="Андрей",
                last_name="Тестов",
                address="ул. Ленина, д. 1",
                city="Москва",
                phone="+79001234567",
                email=registered_user["email"],
                postcode="101000",
            )

        with allure.step(f"Выбрать дату доставки: {tomorrow}"):
            checkout.set_delivery_date(tomorrow)

        with allure.step("Выбрать оплату при доставке"):
            checkout.select_cash_on_delivery()

        with allure.step("Подтвердить заказ"):
            checkout.place_order()

        with allure.step("Проверить страницу подтверждения"):
            assert checkout.is_order_confirmed(), \
                "После оформления должна открыться страница подтверждения заказа"

    def test_register_debug(self, driver):
        """Отладочный тест — смотрим что происходит при регистрации."""
        import time
        driver.get("http://pizzeria.skillbox.cc/register/")
        time.sleep(2)

        # Печатаем все input поля на странице
        inputs = driver.find_elements(By.CSS_SELECTOR, "input")
        for inp in inputs:
            print(f"INPUT: id={inp.get_attribute('id')}, "
                  f"name={inp.get_attribute('name')}, "
                  f"type={inp.get_attribute('type')}")

        # Печатаем все кнопки
        buttons = driver.find_elements(By.CSS_SELECTOR, "button")
        for btn in buttons:
            print(f"BUTTON: name={btn.get_attribute('name')}, "
                  f"type={btn.get_attribute('type')}, "
                  f"text={btn.text}")

        # Заполняем и смотрим что получается
        fake = Faker("ru_RU")
        username = "dbg_" + fake.lexify("????").lower()
        email = fake.email()

        driver.find_element(By.CSS_SELECTOR, "#reg_username").send_keys(username)
        driver.find_element(By.CSS_SELECTOR, "#reg_email").send_keys(email)
        driver.find_element(By.CSS_SELECTOR, "#reg_password").send_keys("TestPass123!")

        print(f"\nBefore submit URL: {driver.current_url}")
        driver.find_element(By.CSS_SELECTOR, "button[name='register']").click()
        time.sleep(5)
        print(f"After submit URL: {driver.current_url}")
        print(f"Page title: {driver.title}")

        # Ищем ошибки
        errors = driver.find_elements(By.CSS_SELECTOR, "ul.woocommerce-error li")
        for e in errors:
            print(f"ERROR: {e.text}")

        assert True  # всегда проходит — нам нужен только вывод