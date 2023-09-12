#!/usr/bin/python3
# coding: utf-8

"""
This module is to download subtitle from stream services.
"""
import os
import sys
import argparse
import logging
import re
from datetime import datetime
import time
from zoneinfo import ZoneInfo
from logging import INFO, DEBUG
from services import service_map
from configs.config import config, app_name, filenames, schedules, __version__
from utils.io import load_toml

def main() -> None:
    """args command"""

    support_services = ', '.join(sorted((service['name'] for service in service_map), key=str.lower))

    parser = argparse.ArgumentParser(
        description="Support auto buy tickets from THSR ticket",
        add_help=False)
    parser.add_argument('service',
                        type=str,
                        help="service name")
    parser.add_argument('-a',
                        '--auto',
                        dest='auto',
                        action='store_true',
                        help="auto pick the ticket")
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

        if schedules[service['name']].get('datetime'):
            schedule_time = schedules[service['name']]['datetime']
            timezone = ZoneInfo('Asia/Taipei')
            current_time = datetime.now(timezone)
            if re.search(r'^\d+:\d+$', schedule_time):
                schedule_time = f"{current_time.date()} {schedule_time}"

            schedule_time = datetime.strptime(schedule_time, '%Y-%m-%d %H:%M').astimezone(timezone)
            logging.info("The bot will auto buy tickets on %s", schedule_time)
            while current_time.time() <= schedule_time.time():
                current_time = datetime.now(ZoneInfo('Asia/Taipei'))
                print(f"\rCurrent time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}", end='', flush=True)
                time.sleep(1)

        start = datetime.now()
        service['class'](args).main()
        logging.info("\n%s took %.3f seconds", app_name, float((datetime.now() - start).total_seconds()))

    else:
        logging.warning("\nOnly support buying ticket from %s ", support_services)
        sys.exit(1)



if __name__ == "__main__":
    main()
