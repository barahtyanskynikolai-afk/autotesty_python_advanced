import allure
import pytest
from pages.bonus_page import BonusPage

# Реальная логика бонусной формы (из JS на странице):
#
# Валидные телефоны: ^[/\+78]+[0-9]{10,10}$
# Примеры: +79001234567, 79001234567, 89001234567
#
# При успехе:
#   1. Появляется alert("Заявка отправлена...")
#   2. Через 6 секунд #bonus_main меняется на "<h3>Ваша карта оформлена!</h3>"
#
# При ошибке:
#   - #bonus_content заполняется текстом ошибки
#   - поле с ошибкой подсвечивается красным (style="border-color:red;")


@allure.epic("Флоу с бонусной системой")
@allure.feature("Форма бонусной программы /bonus/")
class TestBonusFlow:

    @allure.title("TC-17: Успешная регистрация в бонусной программе")
    @allure.description(
        "Ввести корректное имя и телефон в формате +7XXXXXXXXXX, "
        "нажать 'Оформить карту'. Ожидаем alert и через ~6 сек "
        "заголовок 'Ваша карта оформлена!'"
    )
    def test_bonus_registration_success(self, driver):
        bonus = BonusPage(driver)

        with allure.step("Открыть /bonus/"):
            bonus.open_bonus()

        with allure.step("Ввести имя: Андрей"):
            bonus.enter_name("Андрей")

        with allure.step("Ввести телефон: +79001234567"):
            bonus.enter_phone("+79001234567")

        with allure.step("Нажать 'Оформить карту' (alert будет принят автоматически)"):
            bonus.submit_form()

        with allure.step("Дождаться появления 'Ваша карта оформлена!' (~6 сек)"):
            success = bonus.is_success_visible(timeout=10)
            assert success, (
                "После успешной отправки должен появиться заголовок "
                "'Ваша карта оформлена!'"
            )

    @allure.title("TC-18: Ошибка валидации — пустое поле Имя")
    def test_bonus_empty_name(self, driver):
        bonus = BonusPage(driver)

        with allure.step("Открыть /bonus/"):
            bonus.open_bonus()

        with allure.step("Ввести телефон, оставить имя пустым"):
            bonus.enter_phone("+79001234567")

        with allure.step("Нажать 'Оформить карту'"):
            bonus.submit_form()

        with allure.step("Проверить ошибку в #bonus_content"):
            error = bonus.get_error_text()
            assert "Имя" in error, \
                f"Ожидалось сообщение об обязательном поле 'Имя', получили: {error!r}"

        with allure.step("Проверить красную подсветку поля Имя"):
            assert bonus.is_name_field_invalid(), \
                "Поле 'Имя' должно быть подсвечено красным"

    @allure.title("TC-19: Ошибка валидации — пустое поле Телефон")
    def test_bonus_empty_phone(self, driver):
        bonus = BonusPage(driver)

        with allure.step("Открыть /bonus/"):
            bonus.open_bonus()

        with allure.step("Ввести имя, оставить телефон пустым"):
            bonus.enter_name("Андрей")

        with allure.step("Нажать 'Оформить карту'"):
            bonus.submit_form()

        with allure.step("Проверить ошибку в #bonus_content"):
            error = bonus.get_error_text()
            assert "Телефон" in error, \
                f"Ожидалось сообщение об обязательном поле 'Телефон', получили: {error!r}"

        with allure.step("Проверить красную подсветку поля Телефон"):
            assert bonus.is_phone_field_invalid(), \
                "Поле 'Телефон' должно быть подсвечено красным"

    @allure.title("TC-20: Ошибка валидации — оба поля пустые")
    def test_bonus_empty_form(self, driver):
        bonus = BonusPage(driver)

        with allure.step("Открыть /bonus/"):
            bonus.open_bonus()

        with allure.step("Нажать 'Оформить карту' без заполнения"):
            bonus.submit_form()

        with allure.step("Проверить ошибку для поля Имя"):
            error = bonus.get_error_text()
            assert len(error) > 0, \
                "При пустой форме должна появиться ошибка в #bonus_content"

        with allure.step("Проверить красную подсветку поля Имя"):
            assert bonus.is_name_field_invalid(), \
                "Пустое поле 'Имя' должно быть подсвечено красным"

    @allure.title("TC-21: Ошибка валидации — некорректный формат телефона")
    @allure.description(
        "JS проверяет телефон по regex: ^[/\\+78]+[0-9]{10,10}$. "
        "Ввод 'abc12345' не соответствует — ожидаем 'Введен неверный формат телефона'."
    )
    def test_bonus_invalid_phone_format(self, driver):
        bonus = BonusPage(driver)

        with allure.step("Открыть /bonus/"):
            bonus.open_bonus()

        with allure.step("Ввести имя и некорректный телефон 'abc12345'"):
            bonus.enter_name("Андрей")
            bonus.enter_phone("abc12345")

        with allure.step("Нажать 'Оформить карту'"):
            bonus.submit_form()

        with allure.step("Проверить сообщение о неверном формате"):
            error = bonus.get_error_text()
            assert "формат" in error.lower() or "неверн" in error.lower(), \
                f"Ожидалось сообщение о неверном формате, получили: {error!r}"

        with allure.step("Проверить красную подсветку поля Телефон"):
            assert bonus.is_phone_field_invalid(), \
                "Поле 'Телефон' должно быть подсвечено красным при неверном формате"

    @allure.title("TC-22: Ошибка валидации — телефон слишком короткий (5 цифр)")
    def test_bonus_short_phone(self, driver):
        bonus = BonusPage(driver)

        with allure.step("Открыть /bonus/"):
            bonus.open_bonus()

        with allure.step("Ввести имя и слишком короткий телефон"):
            bonus.enter_name("Андрей")
            bonus.enter_phone("12345")

        with allure.step("Нажать 'Оформить карту'"):
            bonus.submit_form()

        with allure.step("Проверить ошибку формата"):
            error = bonus.get_error_text()
            assert len(error) > 0, \
                "Слишком короткий телефон должен вызвать ошибку валидации"

    @allure.title("TC-23: Успешная регистрация с телефоном формата 8XXXXXXXXXX")
    @allure.description(
        "Телефон начинающийся на 8 должен проходить валидацию по regex: "
        "^[/\\+78]+[0-9]{10,10}$"
    )
    def test_bonus_phone_starting_with_8(self, driver):
        bonus = BonusPage(driver)

        with allure.step("Открыть /bonus/"):
            bonus.open_bonus()

        with allure.step("Ввести имя и телефон формата 8XXXXXXXXXX"):
            bonus.enter_name("Мария")
            bonus.enter_phone("89001234567")

        with allure.step("Нажать 'Оформить карту'"):
            bonus.submit_form()

        with allure.step("Дождаться успешной активации"):
            success = bonus.is_success_visible(timeout=10)
            assert success, \
                "Телефон формата 89XXXXXXXXX должен проходить валидацию"