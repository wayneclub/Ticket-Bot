#!/usr/bin/python3
# coding: utf-8

"""
This module is default service
"""
from __future__ import annotations
import ssl
import urllib3
import requests
from configs.config import fields, user_agent
from utils.proxy import get_ip_info, get_proxy

urllib3.disable_warnings()


class BaseService(object):
    """
    BaseService
    """

    def __init__(self, args):
        self.logger = args.log
        self.cookies = {}
        self.config = args.config
        self.service = args.service
        self.fields = fields[self.service]

        self.locale = args.locale
        self.auto = args.auto
        self.list = args.list

        self.session = requests.Session()
        # self.session.mount('https://', TLSAdapter(max_retries=5))
        self.session.headers = {
            'User-Agent': user_agent,
            "Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            "Accept-Language": 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        }

        proxy = args.proxy
        if proxy:
            self.ip_info = get_ip_info()
            self.logger.info(
                'ip: %s (%s)', self.ip_info['ip'], self.ip_info['country'])

            if len("".join(i for i in proxy if not i.isdigit())) == 2:  # e.g. ie, ie12, us1356
                proxy = get_proxy(region=proxy, ip_info=self.ip_info,
                                  geofence=self.GEOFENCE, platform=self.platform)

            self.logger.debug('proxy: %s', proxy)
            if proxy:
                if "://" not in proxy:
                    # assume a https proxy port
                    proxy = f"https://{proxy}"
                self.proxy = proxy
                self.session.proxies.update({"all": proxy})
                self.logger.info(" + Set Proxy")
            else:
                self.logger.info(
                    " + Proxy was skipped as current region matches")


class TLSAdapter(requests.adapters.HTTPAdapter):
    """
    Fix openssl issue
    """

    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        kwargs['ssl_context'] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)
