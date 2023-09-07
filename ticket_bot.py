#!/usr/bin/python3
# coding: utf-8

"""
This module is to download subtitle from stream services.
"""
import argparse
from base64 import b64encode
import logging
from logging import INFO, DEBUG
from datetime import datetime
import ssl
from services import service_map
from configs.config import config, app_name, filenames, __version__
import os
import sys
import requests
from bs4 import BeautifulSoup
from utils.io import load_toml

user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"

def ocr_captcha(img_url):
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    res = requests.get(img_url, headers=headers, timeout=120)
    if res.ok:
        base64_str = b64encode(res.content).decode("utf-8")

        base64_str=base64_str.replace('+', '-').replace('/', '_').replace('=', '')

        url = 'https://ocr.holey.cc/thsrc'
        base64_str = base64_str.replace('+', '-').replace('\/', '_').replace('=+', '')
        data = {'base64_str': base64_str}
        res = requests.post(url, json=data, timeout=5)
        if res.ok:
            return res.json()['data']
        else:
            print(res.text)
    else:
        print(res.text)

class TLSAdapter(requests.adapters.HTTPAdapter):
    """
    Fix openssl issue
    """

    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        kwargs['ssl_context'] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)



def main() -> None:

    support_services = ', '.join(sorted((service['name'] for service in service_map), key=str.lower))

    parser = argparse.ArgumentParser(
        description="Support auto buy tickets from THSR ticket",
        add_help=False)
    parser.add_argument('service',
                        type=str,
                        help="service name")
    parser.add_argument('-l',
                        '--list',
                        dest='list',
                        action='store_true',
                        help="list the tickets")
    parser.add_argument(
        '-locale',
        '--locale',
        dest='locale',
        help="interface language",
    )
    parser.add_argument('-p',
                        '--proxy',
                        dest='proxy',
                        nargs='?',
                        help="proxy")
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help="enable debug logging",
    )
    parser.add_argument(
        '-h',
        '--help',
        action='help',
        default=argparse.SUPPRESS,
        help="show this help message and exit"
    )
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=f'{app_name} {__version__}',
        help="app's version"
    )

    args = parser.parse_args()

    if args.debug:
        os.makedirs(config.directories['logs'], exist_ok=True)
        log_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_file_path = str(filenames.log).format(
            app_name=app_name, log_time=log_time)
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level=logging.DEBUG,
            handlers=[
                logging.FileHandler(log_file_path, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    else:
        logging.basicConfig(
            format='%(message)s',
            level=logging.INFO,
        )

    start = datetime.now()

    service = next((service for service in service_map
                   if args.service.lower() == service['keyword']), None)

    if service:
        log = logging.getLogger(service['class'].__module__)
        if args.debug:
            log.setLevel(DEBUG)
        else:
            log.setLevel(INFO)

        service_config = load_toml(
            str(filenames.config).format(service=service['name']))

        args.log = log
        args.config = service_config
        args.service = service['name']
        service['class'](args).main()
    else:
        logging.warning("\nOnly support buying ticket from %s ", support_services)
        sys.exit(1)

    logging.info("\n%s took %s seconds", app_name,
                 int(float((datetime.now() - start).total_seconds())))


if __name__ == "__main__":
    main()
