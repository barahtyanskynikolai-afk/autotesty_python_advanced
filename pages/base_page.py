from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from utils.logger import get_logger


class BasePage:
    BASE_URL = "http://pizzeria.skillbox.cc"

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.logger = get_logger(self.__class__.__name__)

    def open(self, path: str = ""):
        url = self.BASE_URL + path
        self.logger.info(f"Opening URL: {url}")
        self.driver.get(url)

    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def click(self, locator):
        el = self.wait.until(EC.element_to_be_clickable(locator))
        el.click()

    def type_text(self, locator, text: str):
        el = self.find(locator)
        el.clear()
        el.send_keys(text)

    def get_text(self, locator) -> str:
        return self.find(locator).text.strip()

    def is_visible(self, locator, timeout: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except Exception:
            return False

    def hover(self, locator):
        el = self.find(locator)
        ActionChains(self.driver).move_to_element(el).perform()

    def find_all(self, locator):
        self.wait.until(EC.presence_of_element_located(locator))
        return self.driver.find_elements(*locator)