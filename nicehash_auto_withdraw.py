import requests, time, os, sys
import logging
import http.cookiejar
import imaplib
import re
import nicehash_site_api

spin_wait = 60*10

# Optional

if(len(sys.argv) != 2):
    print("Usage: %s coinbase.email@account.com" % (sys.argv[0]))
    sys.exit(1)

coinbase_account = sys.argv[1]

jar = "data/cookies.txt"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(filename)-20.20s:%(lineno)4d] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler("data/nicehash-autowithdraw.log"),
        logging.StreamHandler(sys.stdout)
    ])

logger = logging.getLogger(__name__)

def spin():

    # Load cookies
    cj = http.cookiejar.MozillaCookieJar(jar)
    cj.load(ignore_expires=True)
    cookies = {c.name:c.value for c in cj}
    #print(cj)

    api = nicehash_site_api.Client(cookies)
    wallet = api.wallet()

    nh_balance = float(wallet['confirmed'])
    logger.info("Nicehash confirmed balance: %f mBTC", nh_balance*1000)

    # Make withdrawl to coinbase
    withdraw_request_id = None
    if(nh_balance > 0.002):

        logger.info("Transferring %f BTC, to coinbase account: %s", nh_balance, coinbase_account)
        api.withdrawal_request(coinbase_account, nh_balance)


def abort(e):
    logger.info("Waiting %s seconds before exit/restart to avoid fast loops", spin_wait)
    time.sleep(spin_wait)
    raise e

if __name__ == "__main__":
    logger.info("Starting Nicehash auto withdraw for Coinbase account: %s", coinbase_account)
    while(True):
        try:
            spin()
        except nicehash_site_api.NicehashAuthException as e:
            logger.error("Nicehash authentication error, quitting: %s", e)
            abort(e)

        except nicehash_site_api.NicehashClientErrorException as e:
            logger.error("Nicehash client error, quitting: %s", e)
            abort(e)

        except nicehash_site_api.NicehashServerErrorException as e:
            logger.error("Nicehash server error, retrying: %s", e)

        except Exception as e:
            logger.error("Unknown error, quitting: %s", e)
            abort(e)
            
        logger.info("Sleeping for %i seconds", spin_wait)
        time.sleep(spin_wait)
