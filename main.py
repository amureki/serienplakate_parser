import os
from time import sleep

from requests_html import HTML, HTMLSession
from telegram import Bot

BASE_URL = 'http://serienplakate.de/'
SLEEP_TIME = os.environ.get('SLEEP_TIME', 5 * 60)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_USER_ID = os.environ.get('TELEGRAM_USER_ID')


class Parser:
    def __init__(self):
        self.session = HTMLSession()

    def get_poster_ids(self):
        response = self.session.get(BASE_URL)
        response.raise_for_status()
        about = response.html.find('.categorie-content', first=True)
        return [p.attrs['data-sid'] for p in about.find('.item')]

    def check_poster_availability(self, poster_id):
        response = self.session.post(
            '{}backend/_ajax.php'.format(BASE_URL),
            data={'cmd': 'poster', 'sId': poster_id}
        )
        response.raise_for_status()
        html = HTML(html=response.json()['data'])
        buttons = html.find('.buttons')
        to_download_elements = [b.find('.download') for b in buttons]
        to_order_elements = [b.find('.noselect') for b in buttons]
        return len(to_download_elements) != len(to_order_elements)

    def notify_via_telegram(self):
        bot = Bot(TELEGRAM_BOT_TOKEN)
        message = 'I\'ve found a free poster to order at {}'.format(BASE_URL)
        bot.send_message(chat_id=TELEGRAM_USER_ID, text=message)

    def run(self):
        poster_ids = self.get_poster_ids()
        order_available = any([self.check_poster_availability(pid) for pid in poster_ids])
        if order_available:
            self.notify_via_telegram()
        return order_available


if __name__ == '__main__':
    parser = Parser()

    while True:
        parser.run()
        sleep(SLEEP_TIME)
