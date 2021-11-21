"""
Code containing spider
"""
import scrapy
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from random import random
from typing import Generator


class DrivingTestSpider(scrapy.Spider):
    """Spider for crawling DVA test booking site. 

    Notes
    -----
    I've used selenium to best mimic human interactions with the site. this will mean the codes a bit heavier than just
    using scrapy form filling etc... but hopefully should avoid any bans.
    """
    def __innit__(
        self,
        licence_number: str,
        test_ref_number: int,
    ):
        self.name = 'driving-test-bot'
        self.start_urls = ['https://queue.driverpracticaltest.dvsa.gov.uk/login']
        self._licence_number = licence_number
        self._test_ref_number = test_ref_number
        self.driver = webdriver.Chrome(executable_path="chromedriver.exe")

    @property
    def licence_number(self):
        """Getter method for the driving licence number variable
        """
        return self._licence_number

    @property
    def test_ref_number(self):
        """Getter method for the test reference number variable
        """
        return self._test_ref_number

    def start_requests(self) -> Generator[str, None, None]:
        """Send request to each start url and pass the response to the parse method of the spider.
        """
        meta = {'dont_redirect': True,
                'handle_httpstatus_list': [301, 302]}

        for url in self.start_urls:
            yield scrapy.Request(url=url, meta=meta, callback=self.parse_forms)

    def parse_forms(
        self,
        response: scrapy.http.Response,
    ):
        """Fill out the form with the users credentials.

        Parameters
        ----------
        response : the response from the initial http request to start_urls.

        Notes
        -----
        Golly what an ugly function. would refactor if only I could be arsed...
        """
        self.get_url_in_driver(url=response.url)
        self.fill_form_box(
            form_xpath="//input[@id='driving-licence-number']",
            input_text=self.licence_number,
        )
        self.fill_form_box(
            form_xpath="//input[@id='application-reference-number']",
            input_text=self.test_ref_number,
            enter=True
        )
        time.sleep(random(1, 3))
        self.find_press_button(button_xpath="//a[@id='date-time-change']")
        time.sleep(random(1, 2))
        self.find_press_button(button_xpath="//input[@id='test-choice-earliest']")
        self.find_press_button(button_xpath="//input[@id='driving-licence-submit']")
        time.sleep(random(1, 2))
        dates_available = {'dates': self.scrape_elements_all_up_yum_yum(
            target_xpath="//li[contains(@class, 'SlotPicker-day') and contains(@id, 'date-2022')]",
            desired_attribute='id'
        )}
        with open('dates.json', 'w') as f:
            json.dump(dates_available, f)  # temporary save lol

    def get_url_in_driver(
        self,
        url: str,
    ):
        """Use webdriver to get url.

        Parameters
        ----------
        url : the url contained in the response object.
        """
        self.driver.get(url)
        time.sleep(random(1, 4))

    def fill_form_box(
        self,
        form_xpath: str,
        input_text: str,
        enter: bool=False,
    ):
        """Fill in a text box with some text for the boys.

        Parameters
        ----------
        form_xpath : Path to form to fill.
        input_text : Text to fill the form to fill with.
        enter : Set True to hit enter after typing.
        """
        textbox = self.driver.find_element(By.XPATH, form_xpath)
        time.sleep(random(1, 4))
        textbox.send_keys(input_text)

        if enter:
            time.sleep(1)
            textbox.send_keys(Keys.ENTER)

    def find_press_button(
        self,
        button_xpath,
    ):
        """Find a button via xpath and then click it.

        Parameters
        ----------
        button_path : Xpath to button.
        """
        button = self.driver.find(By.XPATH, button_xpath)
        time.sleep(random(1, 3))
        try:
            button.click()
        except:
            print('button not clickable!')

    def scrape_elements_all_up_yum_yum(
        self,
        target_xpath: str,
        desired_attribute: str='id',
    ):
        """Scrape elements and put them in a list.

        Parameters
        ----------
        target_xpath : Xpath of desired elements.
        desired_attribute : Attribute you want off the elements.
        """
        elements = self.driver.find_elements(By.XPATH, target_xpath)
        elements = [element.get_attribute(desired_attribute) for element in elements]

        return elements
