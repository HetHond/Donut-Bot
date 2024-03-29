import time

import requests

# Local imports
from .constants import BYBIT_BASE_URL


def get_bybit_market_price(symbol: str) -> float | None:
    endpoint = '/v5/market/tickers'

    response = requests.get(
        BYBIT_BASE_URL + endpoint,
        params={'category': 'linear', 'symbol': symbol}
    )

    if response.status_code != 200:
        # TODO: handle errors
        print(f'HTTP Error while requesting market price for {symbol}')
        return None

    response_json = response.json()
    if response_json.get('retCode') != 0:
        # TODO: handle errors
        print(f'Bybit Error while requesting market price for {symbol}')
        print(f'\tCODE: {response_json.get("retCode")}')
        print(f'\tMSG: {response_json.get("retMsg")}')
        return None
    return float(response_json['result']['list'][0]['markPrice'])


def get_bybit_funding_rate_history(symbol: str,
                                   start_millis: int = 0,
                                   end_millis: int = int(time.time() * 1000)
                                   ) -> (list[dict] | None):
    endpoint = '/v5/market/funding/history'

    response = requests.get(
        BYBIT_BASE_URL + endpoint,
        params={'category': 'linear', 'symbol': symbol, 'startTime': start_millis, 'endTime': end_millis}
    )

    if response.status_code != 200:
        # TODO: handle errors
        print(f'HTTP Error while requesting funding rate history for {symbol}')
        return None

    response_json = response.json()
    if response_json.get('retCode') != 0:
        # TODO: handle errors
        print(f'Bybit Error while requesting funding rate history for {symbol}')
        print(f'\tCODE: {response_json.get("retCode")}')
        print(f'\tMSG: {response_json.get("retMsg")}')
        return None
    return response_json['result']['list']
