import time
import requests

import base64
import hashlib
import hmac

# Local imports
from .constants import KUCOIN_BASE_URL, KUCOIN_FUTURES_BASE_URL, KUCOIN_SYMBOL_TRANSLATION_TABLE


def _translate_symbol(symbol: str) -> str:
    for _from, to in KUCOIN_SYMBOL_TRANSLATION_TABLE.items():
        symbol = symbol.replace(_from, to)
    return symbol


def _generate_headers(endpoint: str, key: str, secret: str, passphrase: str) -> dict:
    now = int(time.time() * 1000)
    str_to_sign = str(now) + 'GET' + endpoint
    signature = base64.b64encode(
        hmac.new(
            secret.encode('utf-8'),
            str_to_sign.encode('utf-8'),
            hashlib.sha256
        ).digest()
    )

    passphrase_ = base64.b64encode(
        hmac.new(
            secret.encode('utf-8'),
            passphrase.encode('utf-8'),
            hashlib.sha256
        ).digest()
    )
    headers = {
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-KEY": key,
        "KC-API-PASSPHRASE": passphrase_,
        "KC-API-KEY-VERSION": "2",
        "Content-Type": "application/json"
    }
    return headers


class KucoinClient:
    # TODO: maybe cache some data to avoid unnecessary requests
    def __init__(self, key: str, secret: str, passphrase: str):
        self.key = key
        self.secret = secret
        self.passphrase = passphrase

    def get_market_price(self, symbol: str) -> float | None:
        symbol = _translate_symbol(symbol)
        endpoint = f'/api/v1/mark-price/{symbol}/current'

        response = requests.get(
            KUCOIN_FUTURES_BASE_URL + endpoint,
            headers=_generate_headers(endpoint=endpoint, key=self.key, secret=self.secret, passphrase=self.passphrase)
        )

        # TODO: repetitive code
        response_json = response.json()
        if response.status_code != 200:
            # TODO: Handle errors
            print(f'HTTP Error while requesting market price for {symbol}')
            print(f'\tCODE: {response_json.get('code')}')
            print(f'\tMSG: {response_json.get('msg')}')
            return None

        if response_json.get('code') != '200000':
            # TODO: Handle error
            print(f'KuCoin Error while requesting market price for {symbol}')
            print(f'\tCODE:{response_json.get('code')}')
            print(f'\tMSG: {response_json.get('msg')}')
            return None

        return response_json['data']['value']

    def get_funding_rate_history(self, symbol: str, start_millis: int=0, end_millis: int=int(time.time()*1000)) -> list | None:
        endpoint = '/api/v1/contract/funding-rates'
        symbol = _translate_symbol(symbol)

        response = requests.get(
            KUCOIN_FUTURES_BASE_URL + endpoint,
            headers=_generate_headers(endpoint=endpoint, key=self.key, secret=self.secret, passphrase=self.passphrase),
            params={'symbol': symbol, 'from': start_millis, 'to': end_millis}
        )

        # TODO: repetitive code
        response_json = response.json()
        if response.status_code != 200:
            # TODO: Handle errors
            print(f'HTTP Error while requesting funding rate history for {symbol}')
            print(f'\tCODE: {response_json.get('code')}')
            print(f'\tMSG: {response_json.get('msg')}')
            return None

        if response_json.get('code') != '200000':
            # TODO: Handle error
            print(f'KuCoin Error while requesting funding rate history for {symbol}')
            print(f'\tCODE:{response_json.get('code')}')
            print(f'\tMSG: {response_json.get('msg')}')
            return None

        return response_json.get('data')
