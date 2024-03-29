GOOGLE_SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

BYBIT_BASE_URL = 'https://api.bybit.com'  # 'https://api-testnet.bybit.com'

KUCOIN_BASE_URL = "https://api.kucoin.com"
KUCOIN_FUTURES_BASE_URL = "https://api-futures.kucoin.com"

KUCOIN_SYMBOL_TRANSLATION_TABLE = {
    'BTC': 'XBT',
    'USDT': 'USDTM'
}

CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "interval": {"type": "number"},
        "spreadsheets": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string"},
                    "worksheet_id": {"type": "number"}
                },
                "required": ["spreadsheet_id", "worksheet_id"],
                "additionalProperties": False
            }
        }
    },
    "required": ["interval", "spreadsheets"],
    "additionalProperties": False
}
