#!/usr/bin/python3
# coding: utf-8

"""
This module is to buy tickets form THSRC
"""

from __future__ import annotations
import base64
import re
import sys
from datetime import date, timedelta
from bs4 import BeautifulSoup
from services.base_service import BaseService
from configs.config import user_agent


class THSRC(BaseService):
    """
    Service code for THSRC (https://irs.thsrc.com.tw/IMINT/).

    """

    def __init__(self, args):
        super().__init__(args)
        # self._ = get_locale(__name__, self.locale)
        self.start_station = self.select_station('start', default_value=self.config['station']['Taipei'])
        self.dest_station = self.select_station('dest', default_value=self.config['station']['Zuouing'])
        self.outbound_date = self.select_date()
        self.outbound_time = self.select_time()
        self.ticket_num = self.select_ticket_num()
        self.train_class = self.select_train_class()
        self.preferred_seat = self.select_preferred_seat()

        self.total = 1

    def print_error_message(self, html_page):
        """Print error messsage"""

        page = BeautifulSoup(html_page, 'html.parser')
        for error_text in page.find_all('span', class_='feedbackPanelERROR'):
            self.logger.error(error_text.text.strip())

    def get_station(self, station_name):
        """Get station value"""

        station_name = station_name.strip().lower().capitalize()

        station_translation = {
            '南港': 'Nangang',
            '台北': 'Taipei',
            '板橋': 'Banqiao',
            '桃園': 'Taoyuan',
            '新竹': 'Hsinchu',
            '苗栗': 'Miaoli',
            '台中': 'Taichung',
            '彰化': 'Changhua',
            '雲林': 'Yunlin',
            '嘉義': 'Chiayi',
            '台南': 'Tainan',
            '左營': 'Zuouing',
        }

        if not re.search(r'[a-zA-Z]+', station_name):
            station_name = station_translation.get(station_name.replace('臺', '台'))

        if self.config['station'].get(station_name):
            return self.config['station'].get(station_name)
        else:
            return None

    def select_station(self, tavel_type: str, default_value: int) -> int:
        """Select start/dest station"""

        if not self.fields[f'{tavel_type}-station']:
            self.logger.info(f"\nSelect {tavel_type} station:")
            for station_name in self.config['station']:
                self.logger.info('%s: %s', self.config['station'][station_name], station_name)

            input_value = input(f"{tavel_type} station (defualt: {default_value}): ").strip()
            return default_value if input_value == '' or not input_value.isdigit() else int(input_value)
        else:
            return self.get_station(self.fields[f'{tavel_type}-station'])

    def select_date(self) -> str:
        """Select date"""

        today = str(date.today())
        # last_avail_date = today + timedelta(days=DAYS_BEFORE_BOOKING_AVAILABLE)
        if not self.fields['outbound-date']:
            input_value = input(f"\nSelect outbound date (defualt: {today}): ")
            return input_value.replace('-', '/') or today.replace('-', '/')
        else:
            return self.fields['outbound-date'].replace('-', '/')

    def select_time(self, default_value: int = 10) -> str:
        """Select time"""

        if not self.fields['outbound-time']:
            self.logger.info('\nSelect outbound time:')
            for idx, t_str in enumerate(self.config['available-timetable'], start=1):
                t_int = int(t_str[:-1])
                if t_str[-1] == "A" and (t_int // 100) == 12:
                    t_int = "{:04d}".format(t_int % 1200)  # type: ignore
                elif t_int != 1230 and t_str[-1] == "P":
                    t_int += 1200

                t_str = str(t_int).zfill(4)
                if t_str == '0001':
                    t_str = '0000'

                self.logger.info(f'{idx}. {t_str[:-2]}:{t_str[-2:]}')

            index = input(f'outbound time (default: {default_value}): ')
            if index=='' or not index.isdigit():
                index = default_value
            else:
                index = int(index)
                if index < 1 or index > len(self.config['available-timetable']):
                    index = default_value
            return self.config['available-timetable'][index-1]
        else:
            t_int = int(self.fields['outbound-time'].replace(':', ''))
            if t_int == 0:
                t_str = '1201A'
            elif t_int == 30:
                t_str = '1230A'
            elif t_int == 1200:
                t_str = '1200N'
            elif t_int == 1230:
                t_str = '1230P'
            elif t_int < 1200:
                t_str = f'{t_int}A'
            else:
                t_str = f'{t_int-1200}P'

            return t_str

    def select_ticket_num(self, default_value: int = 1) -> set:
        """Select ticket number"""

        total = 0
        tickets = list()
        for ticket in self.fields['ticket']:
            ticket_num = int(self.fields['ticket'][ticket])
            total += ticket_num
            if ticket_num > 0:
                tickets.append(f"{ticket_num}{self.config['ticket-type'][ticket]}")
            else:
                tickets.append('')

        if total > self.config['max-ticket-num']:
            self.logger.error("\nYou can only order a maximum of %s tickets!", self.config['max-ticket-num'])
            sys.exit()
        elif total == 0:
            tickets = [f"{default_value}{self.config['ticket-type']['adult']}", '', '', '']
            total = 1

        self.total = total

        return tickets

    def select_train_class(self, default_value: int = 0) -> str:
        """Select class"""

        train_class = self.config['train-class'].get(self.fields['train-class'])

        if not train_class:
            train_class = default_value

        return train_class

    def select_preferred_seat(self, default_value: int = 0) -> str:
        """Select preferred seat"""

        preferred_seat = self.config['preferred-seat'].get(self.fields['preferred-seat'])

        if not preferred_seat:
            preferred_seat = default_value

        return preferred_seat

    def ocr_captcha(self, img_url):
        """OCR captcha"""
        res = self.session.get(img_url, timeout=120)
        if res.ok:
            base64_str = base64.b64encode(res.content).decode("utf-8")
            base64_str=base64_str.replace('+', '-').replace('/', '_').replace('=', '')

            data = {'base64_str': base64_str}

            res = self.session.post(self.config['api']['captcha_ocr'], json=data, timeout=120)
            if res.ok:
                return res.json()['data']
            else:
                self.logger.error(res.text)
                sys.exit(1)
        else:
            self.logger.error(res.text)
            sys.exit(1)

    def get_security_code(self):
        """Get security code from captcha url"""
        self.logger.info("Loading...")

        res = self.session.get(self.config['api']['reservation'], timeout=120, allow_redirects=True)

        if res.ok:
            page = BeautifulSoup(res.text, 'html.parser')
            captcha_url = 'https://irs.thsrc.com.tw' + page.find('img', class_='captcha-img')['src']
            security_code = self.ocr_captcha(captcha_url)
            self.logger.info("+ Security code: %s", security_code)
            jsessionid = res.cookies.get_dict()['JSESSIONID']
            return security_code, jsessionid
        else:
            self.logger.error(res.text)
            sys.exit(1)

    def booking_form(self):
        """1. Fill booking form"""
        security_code, jsessionid = self.get_security_code()
        if not security_code and not jsessionid:
            security_code, jsessionid = self.get_security_code()

        if self.fields['train-no']:
            booking_method = 'radio33'
        else:
            booking_method = 'radio31'

        headers = {
            'Referer': 'https://irs.thsrc.com.tw/IMINT/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': user_agent,
        }

        data = {
            'BookingS1Form:hf:0': '',
            'tripCon:typesoftrip': '0',
            'trainCon:trainRadioGroup': self.train_class,
            'seatCon:seatRadioGroup': self.preferred_seat,
            'bookingMethod': booking_method,
            'selectStartStation': self.start_station,
            'selectDestinationStation': self.dest_station,
            'toTimeInputField': self.outbound_date,
            'backTimeInputField': self.outbound_date,
            'toTimeTable': self.outbound_time,
            'toTrainIDInputField': '',
            'backTimeTable': '',
            'backTrainIDInputField': '',
            'ticketPanel:rows:0:ticketAmount': self.ticket_num[0],
            'ticketPanel:rows:1:ticketAmount': self.ticket_num[1],
            'ticketPanel:rows:2:ticketAmount': self.ticket_num[2],
            'ticketPanel:rows:3:ticketAmount': self.ticket_num[3],
            'homeCaptcha:securityCode': security_code,
            'SubmitButton': 'Search',
            'portalTag': 'false',
            'startTimeForTeenager': '2023/07/01',
            'endTimeForTeenager': '2023/08/31',
            'isShowTeenager': '0',
        }

        form_url = self.config['api']['confirm_train'].format(jsessionid=jsessionid)
        res = self.session.post(
            form_url,
            headers=headers,
            data=data,
            timeout=120,
            allow_redirects=True
        )

        if res.ok:
            return res.text
        else:
            self.logger.error(res.text)
            sys.exit(1)

    def confirm_train(self, html_page, default_value:int = 1):
        """2. Confirm train"""

        select_train_page = BeautifulSoup(html_page, 'html.parser')
        trains = []
        for train in select_train_page.find_all('input', {'name':'TrainQueryDataViewPanel:TrainGroup'}):
            duration = train.parent.findNext('div').find('div', class_='duration').text.replace('\n', '').replace('schedule', '').replace('directions_railway', '').split('｜')
            schedule = duration[0]
            train_no = duration[1]
            discount = train.parent.findNext('div').find('div', class_='discount').text.replace('\n', '')
            trains.append({
                'departure_time' : train['querydeparture'],
                'arrival_time' : train['queryarrival'],
                'duration': schedule,
                'discount': discount,
                'no': train_no,
                'value': train['value']
            })

        self.logger.info('\nSelect train:')
        for idx, train in enumerate(trains, start=1):
            self.logger.info(f"{idx}. {train['departure_time']} -> {train['arrival_time']} ({train['duration']}) | {train['no']}\t{train['discount']}")

        selected_opt = int(input(f'train (default: {default_value}): ') or default_value) -1

        headers = {
            'Referer': 'https://irs.thsrc.com.tw/IMINT/?wicket:interface=:1::',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': user_agent,
        }

        data = {
            'BookingS2Form:hf:0': '',
            'TrainQueryDataViewPanel:TrainGroup': trains[selected_opt]['value'],
            'SubmitButton': 'Confirm',
        }

        res = self.session.post(
            self.config['api']['confirm_ticket'],
            headers=headers,
            data=data,
            timeout=120,
            allow_redirects=True
        )

        if res.ok:
            return res.text
        else:
            self.logger.error(res.text)
            sys.exit(1)

    def confirm_ticket(self, html_page):
        """3. Confirm ticket"""

        if not self.fields['id']:
            roc_id = input("\nInput id: ")
        else:
            roc_id = self.fields['id']

        headers = {
            'Referer': 'https://irs.thsrc.com.tw/IMINT/?wicket:interface=:2::',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': user_agent,
        }

        # non-member: radio44; member: radio46
        if self.fields['tgo-id']:
            ticket_member = 'radio46'
        else:
            ticket_member = 'radio44'

        data = {
            'BookingS3FormSP:hf:0': '',
            'diffOver': '1',
            'isSPromotion': '1',
            'passengerCount': self.total,
            'isGoBackM': '',
            'backHome': '',
            'TgoError': '1',
            'idInputRadio': '0',
            'dummyId': roc_id,
            'dummyPhone': self.fields['phone'],
            'email': self.fields['email'],
            'TicketMemberSystemInputPanel:TakerMemberSystemDataView:memberSystemRadioGroup': ticket_member,
            'TicketMemberSystemInputPanel:TakerMemberSystemDataView:memberSystemRadioGroup:memberShipNumber': self.fields['tgo-id'],
            'agree': 'on',
        }

        res = self.session.post(
            self.config['api']['submit'],
            headers=headers,
            data=data,
            timeout=120,
            allow_redirects=True
        )

        if res.ok:
            if 'pnr-code' in res.text:
                return res.text
            else:
                self.print_error_message(res.text)
        else:
            self.logger.error(res.text)
            sys.exit(1)

    def show_result(self, html_page):
        """4. Show result"""

        result_page = BeautifulSoup(html_page, 'html.parser')
        reservation_no = result_page.find('p', class_='pnr-code').get_text(strip=True)
        payment_deadline = result_page.find('p', class_='payment-status').get_text(strip=True)
        # ticket_num = result_page.find('p', class_='pnr-code').text
        ticket_price = result_page.find('span', id='setTrainTotalPriceValue').get_text(strip=True)

        self.logger.info("\nBooking success!")
        self.logger.info("\n\n----------- Ticket -----------")
        self.logger.info("Reservation No: %s", reservation_no)
        self.logger.info("Payment deadline: %s", payment_deadline)
        # self.logger.info("Count: %s", ticket_num)
        self.logger.info("Price: %s", ticket_price)


    def main(self):
        error = True
        while error:
            confirm_train_page = self.booking_form()
            if 'feedbackPanelERROR' not in confirm_train_page:
                error = False
            else:
                self.print_error_message(confirm_train_page)

        error = True
        while error:
            confirm_ticket_page = self.confirm_train(confirm_train_page)
            if 'feedbackPanelERROR' not in confirm_ticket_page:
                error = False
            else:
                self.print_error_message(confirm_ticket_page)

        error = True
        while error:
            result_page = self.confirm_ticket(confirm_ticket_page)
            if 'feedbackPanelERROR' not in result_page:
                error = False
            else:
                self.print_error_message(result_page)

        self.show_result(result_page)
