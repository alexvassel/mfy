# -*- coding: utf-8 -*-
import argparse
import http.client
import sys
from urllib.parse import urlparse, urljoin

import gevent.monkey
from lxml import html
import requests

from conf import logging, REQUEST_TIMEOUT, REQUEST_EXCEPTIONS
from helpers import Counter, Fetcher

gevent.monkey.patch_socket()


parser = argparse.ArgumentParser()
parser.add_argument('webpage', help='webpage to search images')
args = parser.parse_args()

if __name__ == '__main__':
    jobs = []

    base_url = urlparse(args.webpage)

    logging.info('Started working with {}'.format(base_url.geturl()))

    # Получаем страницу, переданную в параметрах командной строки
    try:
        # TODO выполнять запросы, используя proxy
        response = requests.get(base_url.geturl(), timeout=REQUEST_TIMEOUT)
    except REQUEST_EXCEPTIONS as e:
        logging.error(e)
        sys.exit(1)

    if response.status_code != http.client.OK:
        message = 'Failed to get page {}'.format(base_url.geturl())
        logging.error(message)
        print(message)
        sys.exit(1)

    logging.info('Got page {}'.format(base_url.geturl()))

    page_content = html.document_fromstring(response.content)

    # Находим все изображения с помощью XPATH
    images = page_content.xpath('//img/@src')

    total_images = len(images)
    message = 'Total img tags - {}'.format(total_images)
    logging.info(message)
    print(message)

    counter = Counter(total_images)

    for image_src in images:
        # Получаем урл изображения
        image_url = urlparse(urljoin(base_url.geturl(), image_src))

        fetcher = Fetcher(base_url)

        # Создаем гринлет с задачей по скачиванию изображения
        job = gevent.spawn(fetcher.fetch, image_url)
        jobs.append(job)
        # Когда гринлет закончит работу, counter получит об этом сообщение
        job.link(counter)

    gevent.joinall(jobs)

    print('\nTotal images - {}, downloaded - {}, skipped - {}'.format(total_images,
                                                                      counter.done_tasks,
                                                                      counter.skipped_tasks))

    logging.info('Finished working with {}\n'.format(base_url.geturl()))
