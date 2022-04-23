import os
import pathlib
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By


def file_uri(filename):
    return pathlib.Path(os.path.abspath(filename)).as_uri()


driver = webdriver.Chrome()


class WebpageTests(unittest.TestCase):
    def setUp(self):
        driver.get(file_uri("counter.html"))

    def test_title(self):
        self.assertEqual(driver.title, "Counter")

    def test_increase(self):
        increase = driver.find_element(By.ID, "increase")
        increase.click()
        self.assertEqual(driver.find_element(By.TAG_NAME, "h1").text, "1")

    def test_decrease(self):
        decrease = driver.find_element(By.ID, "decrease")
        decrease.click()
        self.assertEqual(driver.find_element(By.TAG_NAME, "h1").text, "-1")

    def test_multiple_increase(self):
        increase = driver.find_element(By.ID, "increase")
        for i in range(500):
            increase.click()
        self.assertEqual(driver.find_element(By.TAG_NAME, "h1").text, "500")


# if __name__ == "__main__":
#     unittest.main()
