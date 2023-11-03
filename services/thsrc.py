#!/usr/bin/python3
# coding: utf-8

"""
This module is to buy tickets form THSRC
"""

from __future__ import annotations
import base64
import os
import random
import re
import sys
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
import pyperclip
from services.base_service import BaseService
from configs.config import user_agent
from utils.validate import check_roc_id


class THSRC(BaseService):
    """
    Service code for THSRC (https://irs.thsrc.com.tw/IMINT/).
    """

    def __init__(self, args):
        super().__init__(args)
        # self._ = get_locale(__name__, self.locale)
        self.start_station = self.select_station(
            'start', default_value=self.config['station']['Taipei'])
        self.dest_station = self.select_station(
            'dest', default_value=self.config['station']['Zuouing'])
        self.outbound_date = self.select_date()
        self.outbound_time = self.select_time(outbound_date=self.outbound_date)
        self.ticket_num = self.select_ticket_num()
        self.car_type = self.select_car_type()
        self.preferred_seat = self.select_preferred_seat()

    def print_error_message(self, html_page):
        """Print error messsage"""
        page = BeautifulSoup(html_page, 'html.parser')
        for error_text in page.find_all(class_='feedbackPanelERROR'):
            error_message = error_text.text.strip()
            self.logger.error('Error: %s', error_message)
            if '售完' in error_message or '選擇的日期超過目前開放預訂之日期' in error_message or '請選擇' in error_message:
                sys.exit(0)

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
            station_name = station_translation.get(
                station_name.replace('臺', '台'))

        if self.config['station'].get(station_name):
            return self.config['station'].get(station_name)

        self.logger.error('Station not found: %s', station_name)
        sys.exit(1)

    def select_station(self, tavel_type: str, default_value: int) -> int:
        """Select start/dest station"""

        if not self.fields[f'{tavel_type}-station']:
            self.logger.info(f"\nSelect {tavel_type} station:")
            for station_name in self.config['station']:
                self.logger.info(
                    '%s: %s', self.config['station'][station_name], station_name)

            input_value = input(
                f"{tavel_type} station (defualt: {default_value}): ").strip()
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

    def select_time(self, outbound_date: str, default_value: int = 10) -> str:
        """Select time"""

        if not self.fields['outbound-time']:
            self.logger.info('\nSelect outbound time:')
            for idx, t_str in enumerate(self.config['available-timetable'], start=1):
                t_int = int(t_str[:-1])
                if t_str[-1] == "A" and (t_int // 100) == 12:
                    t_int = f"{(t_int % 1200):04d}"  # type: ignore
                elif t_int != 1230 and t_str[-1] == "P":
                    t_int += 1200

                t_str = str(t_int).zfill(4)
                if t_str == '0001':
                    t_str = '0000'

                date_time_str = f'{outbound_date} {t_str[:-2]}:{t_str[-2:]}'

                if datetime.now().timestamp() <= datetime.strptime(
                        date_time_str, "%Y/%m/%d %H:%M").timestamp():
                    self.logger.info(f'{idx}. {date_time_str}')
                else:
                    if idx == default_value:
                        default_value += 1

            index = input(f'outbound time (default: {default_value}): ')
            if index == '' or not index.isdigit():
                index = default_value
            else:
                index = int(index)
                if index < 1 or index > len(self.config['available-timetable']):
                    index = default_value
            return self.config['available-timetable'][index-1]
        else:
            t_int = int(self.fields['outbound-time'].replace(':', ''))
            if t_int % 100 >= 30:
                t_int = int(t_int/100)*100 + 30
            else:
                t_int = int(t_int/100)*100

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
            if ticket_num >= 0:
                tickets.append(
                    f"{ticket_num}{self.config['ticket-type'][ticket]}")
            else:
                tickets.append('')

        if total > self.config['max-ticket-num']:
            self.logger.error(
                "\nYou can only order a maximum of %s tickets!", self.config['max-ticket-num'])
            sys.exit()
        elif total == 0:
            tickets = [
                f"{default_value}{self.config['ticket-type']['adult']}", '', '', '']
        return tickets

    def select_car_type(self, default_value: int = 0) -> str:
        """Select class"""

        car_type = self.config['car-type'].get(self.fields['car-type'])

        if not car_type:
            car_type = default_value

        return car_type

    def select_preferred_seat(self, default_value: int = 0) -> str:
        """Select preferred seat"""

        preferred_seat = self.config['preferred-seat'].get(
            self.fields['preferred-seat'])

        if not preferred_seat:
            preferred_seat = default_value

        return preferred_seat

    def get_security_code(self, captcha_url):
        """OCR captcha, and return security code"""

        res = self.session.get(captcha_url, timeout=200)
        if res.ok:
            base64_str = base64.b64encode(res.content).decode("utf-8")
            base64_str = base64_str.replace(
                '+', '-').replace('/', '_').replace('=', '')

            data = {'base64_str': base64_str}

            res = self.session.post(
                self.config['api']['captcha_ocr'], json=data, timeout=200)
            if res.ok:
                security_code = res.json()['data']
                self.logger.info("+ Security code: %s (%s)",
                                 security_code, captcha_url)
                return security_code
            else:
                self.logger.error(res.text)
                sys.exit(1)
        else:
            self.logger.error(res.text)
            sys.exit(1)

    def get_jsessionid(self):
        """Get jsessionid and security code from captcha url"""
        self.logger.info("\nLoading...")

        res = self.session.get(
            self.config['page']['reservation'], timeout=200, allow_redirects=True)

        if res.ok:
            page = BeautifulSoup(res.text, 'html.parser')
            captcha_url = 'https://irs.thsrc.com.tw' + \
                page.find('img', class_='captcha-img')['src']
            jsessionid = res.cookies.get_dict()['JSESSIONID']
            return jsessionid, captcha_url
        else:
            self.logger.error(res.text)
            sys.exit(1)

    def update_captcha(self, jsessionid):
        """Get security code from captcha url"""
        self.logger.info("Update captcha")

        res = self.session.get(self.config['api']['update_captcha'].format(
            jsessionid=jsessionid, random_value=random.random()), timeout=200)

        if res.ok:
            captcha_url = 'https://irs.thsrc.com.tw' + \
                re.search('src="(.+?)"', res.text).group(1)
            return captcha_url
        else:
            self.logger.error(res.text)
            sys.exit(1)

    def booking_form(self, jsessionid, security_code):
        """1. Fill booking form"""

        if self.fields['train-no']:
            booking_method = 'radio33'
            self.outbound_time = ''
        else:
            booking_method = 'radio31'
            self.fields['train-no'] = ''

        headers = {
            'Referer': 'https://irs.thsrc.com.tw/IMINT/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': user_agent,
        }

        data = {
            'BookingS1Form:hf:0': '',
            'tripCon:typesoftrip': '0',
            'trainCon:trainRadioGroup': self.car_type,
            'seatCon:seatRadioGroup': self.preferred_seat,
            'bookingMethod': booking_method,
            'selectStartStation': self.start_station,
            'selectDestinationStation': self.dest_station,
            'toTimeInputField': self.outbound_date,
            'backTimeInputField': self.outbound_date,
            'toTimeTable': self.outbound_time,
            'toTrainIDInputField': self.fields['train-no'].strip(),
            'backTimeTable': '',
            'backTrainIDInputField': '',
            'ticketPanel:rows:0:ticketAmount': self.ticket_num[0],
            'ticketPanel:rows:1:ticketAmount': self.ticket_num[1],
            'ticketPanel:rows:2:ticketAmount': self.ticket_num[2],
            'ticketPanel:rows:3:ticketAmount': self.ticket_num[3],
            'ticketPanel:rows:4:ticketAmount': self.ticket_num[4],
            'homeCaptcha:securityCode': security_code,
            'SubmitButton': 'Search',
            'portalTag': 'false',
            'startTimeForTeenager': '2023/07/01',
            'endTimeForTeenager': '2023/08/31',
            'isShowTeenager': '0',
        }

        form_url = self.config['api']['confirm_train'].format(
            jsessionid=jsessionid)
        res = self.session.post(
            form_url,
            headers=headers,
            data=data,
            timeout=200,
            allow_redirects=True
        )

        if res.ok:
            return res
        else:
            self.logger.error(res.text)
            sys.exit(1)

    def confirm_train(self, html_page, default_value: int = 1):
        """2. Confirm train"""
        trains = []
        has_discount = False
        for train in html_page.find_all('input', {'name': 'TrainQueryDataViewPanel:TrainGroup'}):
            if not self.fields['inbound-time'] or datetime.strptime(train['queryarrival'], '%H:%M').time() <= datetime.strptime(self.fields['inbound-time'], '%H:%M').time():
                duration = train.parent.findNext('div').find('div', class_='duration').text.replace(
                    '\n', '').replace('schedule', '').replace('directions_railway', '').split('｜')
                schedule = duration[0]
                train_no = duration[1]
                discount = train.parent.findNext('div').find(
                    'div', class_='discount').text.replace('\n', '')
                if discount:
                    has_discount = True

                trains.append({
                    'departure_time': train['querydeparture'],
                    'arrival_time': train['queryarrival'],
                    'duration': schedule,
                    'discount': discount,
                    'no': train_no,
                    'value': train['value']
                })

        if not trains:
            if self.fields['inbound-time']:
                self.logger.info(
                    '\nThere is no trains left on %s before %s, please reserve different outbound time!', self.outbound_date, self.fields['inbound-time'])
            else:
                self.logger.info(
                    '\nThere is no trains left on %s, please reserve other day!', self.outbound_date)
            sys.exit(0)

        self.logger.info('\nSelect train:')

        for idx, train in enumerate(trains, start=1):
            self.logger.info(
                f"{idx}. {train['departure_time']} -> {train['arrival_time']} ({train['duration']}) | {train['no']}\t{train['discount']}")

        if self.list:
            return

        if self.auto:
            if has_discount:
                trains = list(
                    filter(lambda train: train['discount'], trains)) or trains
            if self.fields['inbound-time']:
                trains = list(filter(lambda train: datetime.strptime(self.fields['inbound-time'], '%H:%M') < datetime.strptime(
                    train['arrival_time'], '%H:%M') + timedelta(minutes=20), trains)) or trains

            trains = [min(trains, key=lambda train: datetime.strptime(
                train['duration'], '%H:%M').time())]
            self.logger.info(
                f"\nAuto pick train: {trains[0]['departure_time']} -> {trains[0]['arrival_time']} ({trains[0]['duration']}) | {trains[0]['no']}\t{trains[0]['discount']}")
            selected_opt = 0
        else:
            selected_opt = int(
                input(f'train (default: {default_value}): ') or default_value) - 1

        headers = {
            'Referer': self.config['page']['interface'].format(interface=1),
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
            timeout=200,
            allow_redirects=True
        )

        if res.ok:
            return res
        else:
            self.logger.error(res.text)
            sys.exit(1)

    def confirm_ticket(self, html_page):
        """3. Confirm ticket"""

        dummy_id = self.fields['id']
        if not dummy_id:
            dummy_id = input("\nInput id: ")

        if self.fields['train-no']:
            interface = 1
        else:
            interface = 2

        headers = {
            'Referer': self.config['page']['interface'].format(interface=interface),
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': user_agent,
        }

        candidates = html_page.find_all(
            'input',
            attrs={
                'name': 'TicketMemberSystemInputPanel:TakerMemberSystemDataView:memberSystemRadioGroup'
            },
        )
        if self.fields['tgo-id']:
            ticket_member = candidates[1].attrs['value']
        elif self.fields['tax-id']:
            ticket_member = candidates[2].attrs['value']
        else:
            ticket_member = candidates[0].attrs['value']

        passenger_count = 0
        for ticket in self.ticket_num:
            passenger_count += int(ticket[:-1])

        data = {
            'BookingS3FormSP:hf:0': '',
            'diffOver': '1',
            'isSPromotion': '1',
            'passengerCount': str(passenger_count),
            'isGoBackM': '',
            'backHome': '',
            'TgoError': '1',
            'idInputRadio': '0' if check_roc_id(dummy_id) else '1',
            'dummyId': dummy_id,
            'dummyPhone': self.fields['phone'],
            'email': self.fields['email'],
            'TicketMemberSystemInputPanel:TakerMemberSystemDataView:memberSystemRadioGroup': ticket_member,
            'TicketMemberSystemInputPanel:TakerMemberSystemDataView:memberSystemRadioGroup:memberShipNumber': self.fields['tgo-id'],
            'TicketMemberSystemInputPanel:TakerMemberSystemDataView:memberSystemRadioGroup:GUINumber:': self.fields['tax-id'],
            'agree': 'on',
        }

        disableds = html_page.find_all(
            'input',
            attrs={
                'value': '愛心票'
            },
        )
        for disabled in disableds:
            data[disabled.attrs['name']] = disabled.attrs['value']
            data[disabled.attrs['name'].replace(
                'passengerDataTypeName', 'passengerDataIdNumber')] = input("\nInput disabled id: ")

        elders = html_page.find_all(
            'input',
            attrs={
                'value': '敬老票'
            },
        )
        for elder in elders:
            data[elder.attrs['name']] = elder.attrs['value']
            data[elder.attrs['name'].replace(
                'passengerDataTypeName', 'passengerDataIdNumber')] = input("\nInput elder id: ")

        res = self.session.post(
            self.config['api']['submit'].format(interface=interface),
            headers=headers,
            data=data,
            timeout=200,
            allow_redirects=True
        )

        if res.ok:
            return res
        else:
            self.logger.error(res.text)
            sys.exit(1)

    def print_result(self, html_page):
        """4. Print result"""

        reservation_no = html_page.find(
            'p', class_='pnr-code').get_text(strip=True)
        payment_status = html_page.find(
            'p', class_='payment-status').get_text(strip=True)
        car_type = html_page.find(
            'div', class_='car-type').find('p', class_='info-data').get_text(strip=True)
        ticket_type = html_page.find(
            'div', class_='ticket-type').find('div').get_text(strip=True)
        ticket_price = html_page.find(
            'span', id='setTrainTotalPriceValue').get_text(strip=True)
        card = html_page.find('div', class_='ticket-card')
        onbound_date = card.find('span', class_='date').get_text(strip=True)
        train_no = card.find('span', id='setTrainCode0').get_text(strip=True)
        departure_time = card.find(
            'p', class_='departure-time').get_text(strip=True)
        departure_station = card.find(
            'p', class_='departure-stn').get_text(strip=True)
        arrival_time = card.find(
            'p', class_='arrival-time').get_text(strip=True)
        arrival_station = card.find(
            'p', class_='arrival-stn').get_text(strip=True)
        duration = card.find(
            'span', id='InfoEstimatedTime0').get_text(strip=True)
        seats = [seat.get_text(strip=True) for seat in html_page.find(
            'div', class_='detail').find_all('div', class_='seat-label')]

        self.logger.info("\nBooking success!")
        self.logger.info(
            "\n---------------------- Ticket ----------------------")
        self.logger.info("Reservation No: %s", reservation_no)
        self.logger.info("Payment Status: %s", payment_status)
        self.logger.info("Car Type: %s", car_type)
        self.logger.info("Ticket Type: %s", ticket_type)
        self.logger.info("Price: %s", ticket_price)
        self.logger.info(
            "----------------------------------------------------")
        self.logger.info("Date: %s", onbound_date)
        self.logger.info("Train No: %s", train_no)
        self.logger.info("Duration: %s", duration)
        self.logger.info("%s (%s) -> %s (%s)", departure_time,
                         departure_station, arrival_time, arrival_station)
        self.logger.info(
            "----------------------------------------------------")
        self.logger.info("Seats: %s", ', '.join(seats))
        self.logger.info(
            "\n\nGo to the reservation record to confirm the ticket and pay!\n (%s) ", self.config['page']['history'])

        if not os.getenv("COLAB_RELEASE_TAG"):
            pyperclip.copy(reservation_no)
            self.logger.info("\nReservation No. has been copied to clipboard!")

    def main(self):
        """Buy ticket process"""

        jsessionid = ''
        captcha_url = ''
        while not jsessionid and not captcha_url:
            jsessionid, captcha_url = self.get_jsessionid()

        result_url = ''
        while result_url != self.config['page']['interface'].format(interface=1):
            security_code = self.get_security_code(captcha_url)
            booking_form_result = self.booking_form(jsessionid, security_code)
            result_url = booking_form_result.url

            if result_url != self.config['page']['interface'].format(interface=1):
                self.print_error_message(booking_form_result.text)

                if '檢測碼輸入錯誤' in booking_form_result.text:
                    captcha_url = self.update_captcha(jsessionid=jsessionid)

        confirm_train_page = BeautifulSoup(
            booking_form_result.text, 'html.parser')

        if not self.fields['train-no']:
            result_url = ''
            while result_url != self.config['page']['interface'].format(interface=2):
                confirm_train_result = self.confirm_train(confirm_train_page)
                if self.list:
                    return
                result_url = confirm_train_result.url

                if result_url != self.config['page']['interface'].format(interface=2):
                    self.print_error_message(booking_form_result.text)

            confirm_ticket_page = BeautifulSoup(
                confirm_train_result.text, 'html.parser')
            interface = 3
        else:
            confirm_ticket_page = confirm_train_page
            interface = 2

        result_url = ''
        while result_url != self.config['page']['interface'].format(interface=interface):
            confirm_ticket_result = self.confirm_ticket(confirm_ticket_page)
            result_url = confirm_ticket_result.url

            if result_url != self.config['page']['interface'].format(interface=interface):
                self.print_error_message(booking_form_result.text)

        result_page = BeautifulSoup(confirm_ticket_result.text, 'html.parser')
        self.print_result(result_page)
