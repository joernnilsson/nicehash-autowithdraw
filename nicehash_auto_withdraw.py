import requests, time, os, sys
import logging
import http.cookiejar
import imaplib
import re
import nicehash
import json

spin_wait = 60*10

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(filename)-20.20s:%(lineno)4d] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ])

logger = logging.getLogger(__name__)

def spin(coinbase_account, organisation_id, key, secret):

    host = 'https://api2.nicehash.com'

    private_api = nicehash.private_api(host, organisation_id, key, secret, True)

    my_btc_account = private_api.get_accounts_for_currency("BTC")

    nh_balance = my_btc_account['balance']


    nh_balance = float(my_btc_account['balance'])
    logger.info("Nicehash confirmed balance: %f mBTC", nh_balance*1000)

    # Make withdrawl to coinbase
    withdraw_request_id = None
    if(nh_balance > 0.002):

        # Get address ids
        withdrawal_addresses = private_api.get_withdrawal_addresses("BTC", 100, 0)

        print(withdrawal_addresses)

        for wa in withdrawal_addresses['list']:
            if wa["type"]["code"] == "COINBASE" and wa["address"] == coinbase_account:
                logger.info("Transferring %f BTC, to coinbase account: %s", nh_balance, coinbase_account)
                res = private_api.withdraw_request(wa["id"], nh_balance, "BTC")
                print(res)
                break


def abort(e):
    logger.info("Waiting %s seconds before exit/restart to avoid fast loops", spin_wait)
    time.sleep(spin_wait)
    raise e

def env(key):
    if key in os.environ:
        return os.environ[key]
    else:
        return None

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description='Withdraw BTC funds to Coinbase account')
    parser.add_argument("--coinbase-account", '-c', help='Coinbase account email address [COINBASE_ACCOUNT]')
    parser.add_argument("--nicehash-organization", '-o', help='Nicehash organization id [NICEHASH_ORGANIZATION]')
    parser.add_argument("--nicehash-api-key", '-k', help='Nicehash API key [NICEHASH_API_KEY]')
    parser.add_argument("--nicehash-api-secret", '-s', help='Nicehash API secret [NICEHASH_API_SECRET]')

    args = parser.parse_args()

    coinbase_account = args.coinbase_account if args.coinbase_account else env("COINBASE_ACCOUNT")
    nicehash_organization = args.nicehash_organization if args.nicehash_organization else env("NICEHASH_ORGANIZATION")
    nicehash_api_key = args.nicehash_api_key if args.nicehash_api_key else env("NICEHASH_API_KEY")
    nicehash_api_secret = args.nicehash_api_secret if nicehash_api_secret.nicehash_secret else env("NICEHASH_API_SECRET")

    if not(coinbase_account and nicehash_organization and nicehash_key and nicehash_secret):
        parser.error("All parameters are required")        

    logger.info("Starting Nicehash auto withdraw for Coinbase account: %s", coinbase_account)
    while(True):
        try:
            spin(coinbase_account, nicehash_organization, nicehash_api_key, nicehash_api_secret)

        except Exception as e:
            logger.error("Unknown error, quitting: %s", e)
            abort(e)
            
        logger.info("Sleeping for %i seconds", spin_wait)
        time.sleep(spin_wait)
