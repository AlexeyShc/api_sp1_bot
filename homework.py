import os
import time
import logging

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(message)s')


TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
HEADERS = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}',}
URL_API_PRAKTIKUM = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework_name is None:
        return 'У вас проверили работу, но ее название отсутсвует в ответе от сервера'
    status = homework.get('status')
    if status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif status == 'approved':
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    else:
        return 'У вас проверили работу, но статус работы оказался непредусмотрен'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_time):
    current_time = current_time or int(time.time())
    params = {
        'from_date': current_time,
    }
    try:
        homework_statuses = requests.get(URL_API_PRAKTIKUM, headers=HEADERS, params=params)
        return homework_statuses.json()
    except (ConnectionError, TimeoutError, ValueError) as e:
        logging.exception(e)
        return {}


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]), bot_client)
            current_timestamp = new_homework.get('current_date', current_timestamp)
            time.sleep(900)

        except Exception as e:
            print(f'Бот столкнулся с ошибкой: {e}')
            logging.exception(e)
            time.sleep(5)


if __name__ == '__main__':
    main()
