import datetime

import gspread

# Local imports
from .kucoin import KucoinClient
from .bybit import *


class DonutBot:
    def __init__(self, kucoin_key: str, kucoin_secret: str, kucoin_passphrase: str):
        self.kucoin_client = KucoinClient(key=kucoin_key, secret=kucoin_secret, passphrase=kucoin_passphrase)

    def timestamp(self, worksheet: gspread.Worksheet, row: int, col: int):
        worksheet.update_cell(row, col, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # TODO: specify data positions
    def update_sheet(self, worksheet: gspread.Worksheet):
        cells_to_update = []

        row_values = worksheet.row_values(2)[1:]
        for i, ticker in enumerate(row_values):
            # Skip all un-even columns
            if i % 2:
                continue

            # Quit trying when a blank space is found in an even column
            if not ticker:
                break

            row = 3
            col = i + 2

            # Bybit market price
            bybit_market_price = get_bybit_market_price(ticker + 'USDT')
            if bybit_market_price is not None:
                cells_to_update.append(gspread.Cell(
                    row, col,
                    value=bybit_market_price
                ))
            row += 1

            # Bybit funding rates
            bybit_funding_rates = get_bybit_funding_rate_history(ticker + 'USDT')
            if bybit_funding_rates is not None:
                # Remove excess data
                bybit_funding_rates = [float(fr['fundingRate']) * 100 for fr in bybit_funding_rates]

                # Cut off everything past 100 entries
                bybit_funding_rates = bybit_funding_rates[:min(100, len(bybit_funding_rates))]

                # Format all funding rates to have 4 decimals
                bybit_funding_rates = [f'{fr:.4f}' for fr in bybit_funding_rates]

                for fr in bybit_funding_rates:
                    cells_to_update.append(gspread.Cell(
                        row, col,
                        value=f'{fr}%'
                    ))
                    row += 1

            # Next column
            col += 1
            row = 3

            # Kucoin market price
            kucoin_market_price = self.kucoin_client.get_market_price(ticker + 'USDT')
            if kucoin_market_price is not None:
                cells_to_update.append(gspread.Cell(
                    row, col,
                    value=kucoin_market_price
                ))
            row += 1

            # Kucoin funding rates
            kucoin_funding_rates = self.kucoin_client.get_funding_rate_history(ticker + 'USDT')
            if kucoin_funding_rates is not None:
                # Remove excess data
                kucoin_funding_rates = [float(fr['fundingRate']) * 100 for fr in kucoin_funding_rates]

                # Cut off everything past 100 entries
                kucoin_funding_rates = kucoin_funding_rates[:min(100, len(kucoin_funding_rates))]

                # Format all funding rates to have 4 decimals
                kucoin_funding_rates = [f'{fr:.4f}' for fr in kucoin_funding_rates]

                for fr in kucoin_funding_rates:
                    cells_to_update.append(gspread.Cell(
                        row, col,
                        value=f'{fr}%'
                    ))
                    row += 1

        if cells_to_update:
            worksheet.update_cells(cells_to_update)
