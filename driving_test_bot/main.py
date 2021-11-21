"""
Run the bloody thing boi.
"""
import yaml
import json
import yagmail
from datetime import datetime
from typing import List
from spider_crawler import DrivingTestSpider
from scrapy.crawler import CrawlerProcess


with open('config.yaml') as f:
    CREDENTIALS = yaml.safe_load(f)


def main() -> None:
    """Runs whole project all at once oh wow!
    """
    scrape_driving_tests()
    dates = read_clean_json()

    earliest = min(dates)
    if earliest < datetime.strptime(CREDENTIALS['current_test_date'], '%Y-%m-%d'):
        new_date = earliest.strftime('%d/%m/%Y')
        send_email(new_date=new_date)


def scrape_driving_tests() -> None:
    """Run scrape on the target site.

    Notes
    -----
    Instantiates twisted reactor, and closes the reactor down at the end of the process. As such no further use of
    twisted will be allowed in the process after this point.
    """
    process = CrawlerProcess()
    process.crawl(
        DrivingTestSpider,
        licence_number=CREDENTIALS['licence_number'],
        test_ref_number=CREDENTIALS['test_ref_number']
    )
    process.start()


def read_clean_json() -> List[datetime.datetime]:
    """Read in scraped dates and convert to datetime objs.

    Returns
    -------
    List[datetime.datetime]
        List of dates.
    """
    with open('dates.json') as f:
        data = json.load(f)

    data = [datetime.strptime(date.replace('date-', ''), '%Y-%m-%d') for date in data['dates']]

    return data


def send_email(new_date: str):
    """Use yagmail to send yourself an email about the new test date.

    Parameters
    ----------
    new_date : The new earliest test date available.
    """
    yag = yagmail.SMTP(CREDENTIALS['email_address'], CREDENTIALS["email_password"])

    html_msg = f"""<p>Hi!<br>
                Theres an earlier test date available for your driving test<br>
                it is on {new_date}<br>
                does this please your highness?</p>"""

    yag.send(CREDENTIALS['email_address'], "earlier test date available", html_msg)


if __name__ == '__main__':
    print('pizza time')
    main()