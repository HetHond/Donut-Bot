import gspread

# Local imports
from .kucoin import KucoinClient
from .bybit import *


class DonutBot:
    def __init__(self, kucoin_key: str, kucoin_secret: str, kucoin_passphrase: str):
        self.kucoin_client = KucoinClient(key=kucoin_key, secret=kucoin_secret, passphrase=kucoin_passphrase)

    # TODO: specify data positions
    def update_sheet(self, worksheet: gspread.Worksheet):
        tickers = worksheet.col_values(1)[1:]

        cells_to_update = []
        for i, ticker in enumerate(tickers):
            if not ticker:
                continue

            row = i+2
            col = 2

            # Bybit market price
            bybit_market_price = get_bybit_market_price(ticker + 'USDT')
            if bybit_market_price is not None:
                cells_to_update.append(gspread.Cell(
                    row, col,
                    value=bybit_market_price
                ))
            col += 1

            # Kucoin market price
            kucoin_market_price = self.kucoin_client.get_market_price(ticker + 'USDT')
            if kucoin_market_price is not None:
                cells_to_update.append(gspread.Cell(
                    row, col,
                    value=kucoin_market_price
                ))
            col += 1

            bybit_funding_rates = get_bybit_funding_rate_history(ticker + 'USDT')
            if bybit_funding_rates is not None:
                for j in range(min((3, len(bybit_funding_rates)))):
                    cells_to_update.append(gspread.Cell(
                        row, col,
                        value=float(bybit_funding_rates[j]['fundingRate'])
                    ))
                    col += 1

            kucoin_funding_rates = self.kucoin_client.get_funding_rate_history(ticker + 'USDT')
            if kucoin_funding_rates is not None:
                for j in range(min((3, len(kucoin_funding_rates)))):
                    cells_to_update.append(gspread.Cell(
                        row, col,
                        value=float(kucoin_funding_rates[j]['fundingRate'])
                    ))
                    col += 1

        worksheet.update_cells(cells_to_update)
