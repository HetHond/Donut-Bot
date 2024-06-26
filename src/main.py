import argparse
import sys
import os
import json
import time
import logging

from jsonschema import validate
from jsonschema.exceptions import ValidationError

# Local imports
from .donut_bot import DonutBot
from .sheets_client import get_gspread_with_service_account, get_gspread_client_with_auth
from .constants import GOOGLE_SHEETS_SCOPES, CONFIG_SCHEMA

logger = logging.getLogger(__name__)


def get_config(config_path):
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
            validate(instance=config, schema=CONFIG_SCHEMA)
            return config
    except FileNotFoundError:
        logger.critical("Configuration file not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.critical("Error deserializing the configuration file.")
        sys.exit(1)
    except ValidationError as e:
        logger.critical("Error while validating configuration file: ", e)
        sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(description="Google Spreadsheets Donut-Bot Application")
    parser.add_argument('--config', help='Path to the config file', default='./config.json')
    parser.add_argument('--service-account', action='store_true', help='Use a service account instead of OAuth')
    parser.add_argument('--service-account-path', help='Path to the service account key json', default='./service-account-credentials.json')
    parser.add_argument('--google-credentials-path', help='Path to the Google credentials file', default=os.environ.get('GOOGLE_CREDENTIALS_PATH'))
    parser.add_argument('--kucoin-api-key', help='Kucoin API key', default=os.environ.get('KUCOIN_API_KEY'))
    parser.add_argument('--kucoin-api-secret', help='Kucoin API secret', default=os.environ.get('KUCOIN_API_SECRET'))
    parser.add_argument('--kucoin-api-passphrase', help='Kucoin API passphrase', default=os.environ.get('KUCOIN_API_PASSPHRASE'))
    return parser.parse_args()


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    args = parse_args()
    config = get_config(args.config)
    logger.info('Read and validated configuration file.')

    donut_bot = DonutBot(
        kucoin_key=args.kucoin_api_key,
        kucoin_secret=args.kucoin_api_secret,
        kucoin_passphrase=args.kucoin_api_passphrase
    )
    logger.info('Initiated donut bot.')

    if args.service_account:
        gclient = get_gspread_with_service_account(args.service_account_path, scopes=GOOGLE_SHEETS_SCOPES)
    else:
        gclient = get_gspread_client_with_auth(args.google_credentials_path, scopes=GOOGLE_SHEETS_SCOPES)

    worksheets = [gclient.open_by_key(sheet['spreadsheet_id']).get_worksheet_by_id(sheet['worksheet_id']) for sheet in config['spreadsheets']]

    logger.info('Starting loop.')
    while True:
        last_timestamp = time.time()
        for worksheet in worksheets:
            logger.info(f'Updating worksheet with id {worksheet.id} inside of {worksheet.spreadsheet.title}.')
            donut_bot.update_sheet(worksheet)
            donut_bot.timestamp(worksheet, 1, 1)
            logger.info(f'Updated worksheet with id {worksheet.id} inside of {worksheet.spreadsheet.title}.')

        logger.debug(f'Waiting for {config["interval"]} seconds.')
        while (time.time() - last_timestamp) < config['interval']:
            pass
