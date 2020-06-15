import json
import hmac
import hashlib
import time
import requests
import base64
import os

from requests.auth import AuthBase
from ratelimit import limits, sleep_and_retry
from datetime import datetime, timedelta

API_URL = 'https://api.pro.coinbase.com/'


class Coinbase:
    def __init__(self, api_url=API_URL):
        self.api_url = api_url
        self.products = self._get('products')

    @sleep_and_retry
    @limits(calls=3, period=1)
    def _get(self, path, params=None):
        return requests.get(
            self.api_url + path,
            params=params
        ).json()

    def marketVolume(self):
        return {
            p['id'].replace('-', '_'): {
                p['base_currency']: 0,
                p['quote_currency']: 0
            } for p in self.products
        }

    def marketTicker(self):
        tickers = [
            self._get("products/%s/ticker" % p['id']) for p in self.products
        ]

        return {
            p['id'].replace('-', '_'): {
                'last': t['price']
            } for p, t in zip(self.products, tickers)
        }

    def marketStatus(self):
        currencies = self._get('currencies')

        return {c['id']: c for c in currencies}

    def marketChart(self, pair, start, period, end):
        indices = [
            datetime.fromtimestamp(time)
            for time in range(int(start), int(end), period*300)
        ]
        indices.append(datetime.fromtimestamp(end))

        chart = []
        for start_dt, end_dt in zip(indices[:-1], indices[1:]):
            result = self._get(
                "products/%s/candles" % pair.replace('_', '-'),
                params={
                    'start': start_dt.isoformat(),
                    'end': end_dt.isoformat(),
                    'granularity': period
                }
            )
            chart.extend(result)

        return [
            {
                'volume': c[5],
                'quoteVolume': c[5],
                'weightedAverage': (c[2] + c[1]) / 2,
                'close': c[4],
                'low': c[1],
                'high': c[2],
                'date': c[0],
                'open': c[3]
            }
            for c in chart
        ]
