# -*- coding: utf-8 -*-

import http.client
import os
import requests
import shutil

from conf import REQUEST_TIMEOUT, logging, REQUEST_EXCEPTIONS, IMAGES_TYPES, IMAGES_DIR


class Counter:
    """Подсчет статистики для отображения прогресса выполнения задач"""
    done_tasks = 0
    skipped_task = 0

    def __init__(self, total_tasks):
        self.total_tasks = total_tasks

    def __call__(self, greenlet):
        """Callback для gevent
        Вызывается после завершения работы по получению изображения"""
        if greenlet.value is not None:
            self.done_tasks += 1
        else:
            self.skipped_task += 1

        message = '{} of {} image(s) downloaded (skipped {})'.format(self.done_tasks,
                                                                     self.total_tasks,
                                                                     self.skipped_task)
        print(message)
        logging.info(message)


class Fetcher:
    """Работа по получению и сохранению изображения"""
    response = None

    def __init__(self, base_url):
        self.base_url = base_url

    def fetch(self, image_url):
        """Получение изображения по урлу"""
        try:
            self.response = requests.get(image_url.geturl(), timeout=REQUEST_TIMEOUT, stream=True)

            # Ответ 200?
            if self.response.status_code != http.client.OK:
                message = 'Failed to get page {} with status {}'.format(image_url,
                                                                        self.response.status_code)
                logging.error(message)
                return

            # У ответа верный Content-Type?
            if not self._is_response_image():
                logging.info('{} is not image'.format(image_url.geturl()))
                return

            # Сохранение изображения
            try:
                filename = self._create_filename(image_url)
                self._save_file(filename)
            except OSError:
                message = 'Failed to save image {}'.format(image_url.geturl())
                logging.error(message)
                return

            return self.response

        except REQUEST_EXCEPTIONS as e:
            logging.error(e)

    def _save_file(self, filename):
        """Сохранение файла чанками во избежание переполнения памяти"""
        with open(filename, 'wb') as f:
            shutil.copyfileobj(self.response.raw, f)

    def _is_response_image(self):
        """Проверка на то, что у ответа на запрос изображения стоит верный Content-Type"""
        if self.response.headers.get('Content-Type') is None:
            return False

        maintype = self.response.headers['Content-Type'].split(';')[0].lower()
        if maintype not in IMAGES_TYPES:
            return False

        return True

    def _create_filename(self, image_url):
        """Создание имени файла и директорий для него
        директория внутри проекта - IMAGES_DIR
        затем имя хоста из адреса командной строки
        затем имя хоста изображения
        схема хранения файлов как на веб-сервере
        """
        filename = (IMAGES_DIR + self.base_url.hostname + '/' +
                    image_url.netloc + '/' + image_url.path)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        return filename
