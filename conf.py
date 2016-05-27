# -*- coding: utf-8 -*-
import logging
import requests

LOG_FILE = 'app.log'

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S %z')

REQUEST_TIMEOUT = 5  # Секунд

REQUEST_EXCEPTIONS = (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema,
                      requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError,
                      requests.exceptions.ReadTimeout)

IMAGES_TYPES = ('image/png', 'image/jpeg', 'image/gif')

IMAGES_DIR = 'images/'
