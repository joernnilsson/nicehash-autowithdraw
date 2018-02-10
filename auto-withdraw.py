import requests, time, os, sys
import logging
import http.cookiejar
import imaplib
import re
import nicehash_site_api

spin_wait = 60*10
coinbase_account = os.getenv('COINBASE_ACCOUNT')

# Optional
gmail_username = os.getenv('GMAIL_USERNAME')
gmail_password = os.getenv('GMAIL_PASSWORD')

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
        resp = api.withdrawal_request(coinbase_account, nh_balance)

        withdraw_request_id = resp['withdraw_request_id']
        logger.info("Sleeping 25 sec to wait for email")
        time.sleep(25)

    if(withdraw_request_id == None and len(wallet['withdraw_requests']) > 0):
        withdraw_request_id = wallet['withdraw_requests'][0]["id"]

    # Try to confirm the withdrawal by reading the email
    if(withdraw_request_id != None and gmail_username):
        logger.info("Checking gmail inbox for confirmation code")

        imap = imaplib.IMAP4_SSL('imap.gmail.com')
        imap.login(gmail_username, gmail_password)
        imap.select("inbox", readonly=True)
        result, data = imap.search(None, "ALL")
        ids = data[0]
        id_list = ids.split()
        id_list = list(reversed(id_list))
        key = None
        for mid in id_list:
            result, data = imap.fetch(mid, "(RFC822)")
            raw = data[0][1].decode("utf-8") 
            if(raw.find("Withdrawal confirmation") > 0):
                start = re.search(r"[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}", raw).start()
                if(start>0):
                    key = raw[start:start+36]
                    logger.info("Found confirmation key in email: %s",key)
                else:
                    logger.error("Found confirmation email, but could not match th key")
                    logger.debug(raw)
                break
        
        if(key != None):

            # Confirm withdrawal
            logger.info("Confirming withdrawal %i, to coinbase account: %s", withdraw_request_id, coinbase_account)
            api.withdrawal_confirm(withdraw_request_id, key)

            
if __name__ == "__main__":
    logger.info("Starting Nicehash auto withdraw for Coinbase account: %s", coinbase_account)
    while(True):
        try:
            spin()
        except nicehash_site_api.NicehashAuthException as e:
            logger.error("Nicehash authentication error, quitting: %s", e)
            logger.info("Waiting %s seconds before exit/restart to avoid fast loops", spin_wait)
            time.sleep(spin_wait)
            raise e
        except nicehash_site_api.NicehashClientErrorException as e:
            logger.error("Nicehash client error, quitting: %s", e)
            logger.info("Waiting %s seconds before exit/restart to avoid fast loops", spin_wait)
            time.sleep(spin_wait)
            raise e
        except nicehash_site_api.NicehashServerErrorException as e:
            logger.error("Nicehash server error, retrying: %s", e)
        except Exception as e:
            logger.error("Unknown error, quitting: %s", e)
            logger.info("Waiting %s seconds before exit/restart to avoid fast loops", spin_wait)
            time.sleep(spin_wait)
            raise e
            
        logger.info("Sleeping for %i seconds", spin_wait)
        #break
        time.sleep(spin_wait)
