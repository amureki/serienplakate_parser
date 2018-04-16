import os
from time import sleep

import requests
from requests_html import HTML, HTMLSession
from telegram import Bot

BASE_URL = 'http://serienplakate.de/'
SLEEP_TIME = os.environ.get('SLEEP_TIME', 10 * 60)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_USER_ID = os.environ.get('TELEGRAM_USER_ID')
HEALTHCHECK_TOKEN = os.environ.get('HEALTHCHECK_TOKEN')


class Parser:
    def __init__(self):
        self.session = HTMLSession()

    def get_poster_ids(self):
        response = self.session.get(BASE_URL)
        response.raise_for_status()
        about = response.html.find('.categorie-content', first=True)
        return [p.attrs['data-sid'] for p in about.find('.item')]

    def check_poster_availability(self, poster_id) -> int:
        """Check if there are available posters to order. Method returns quantity."""
        response = self.session.post(
            '{}backend/_ajax.php'.format(BASE_URL),
            data={'cmd': 'poster', 'sId': poster_id}
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            self.send_telegram_message(message='{} errored:{}'.format(BASE_URL, e))
            raise

        html = HTML(html=response.json()['data'])
        quantity_block = html.find('.count')[0]
        quantity_proportion = quantity_block.text.split(' ')[0]
        quantity_available = int(quantity_proportion.split('/')[0])
        return quantity_available

    def send_telegram_message(self, message):
        bot = Bot(TELEGRAM_BOT_TOKEN)
        bot.send_message(chat_id=TELEGRAM_USER_ID, text=message)

    def run(self):
        poster_ids = self.get_poster_ids()
        order_available = any([self.check_poster_availability(pid) > 0 for pid in poster_ids])
        if order_available:
            message = 'I\'ve found a free poster to order at {}'.format(BASE_URL)
            self.send_telegram_message(message=message)
        return order_available


if __name__ == '__main__':
    parser = Parser()

    while True:
        parser.run()
        sleep(int(SLEEP_TIME))
        if HEALTHCHECK_TOKEN:
            requests.get('https://hchk.io/{}'.format(HEALTHCHECK_TOKEN))
