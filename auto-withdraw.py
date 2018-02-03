import requests, time, os, sys
import logging
import http.cookiejar
import imaplib
import re

spin_wait = 60*10
coinbase_account = os.getenv('COINBASE_ACCOUNT')

# Optional
gmail_username = os.getenv('GMAIL_USERNAME')
gmail_password = os.getenv('GMAIL_PASSWORD')

jar = "data/cookies.txt"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler("data/nicehash-autowithdraw.log"),
        logging.StreamHandler(sys.stdout)
    ])

logger = logging.getLogger(__name__)

import pickle
def save_cookies(requests_cookiejar, filename):
    with open(filename, 'wb') as f:
        pickle.dump(requests_cookiejar, f)

def load_cookies(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

class NicehashException(Exception):
    def __init__(self, response):
        self.response = response
        self.status_code = response.status_code
    def __str__(self):
        return 'NicehashException: %s %s' % (str(self.status_code), self.response.text)

class NicehashAuthException(NicehashException): pass
class NicehashServerErrorException(NicehashException): pass
class NicehashClientErrorException(NicehashException): pass

def verifyResponse(response):
    data = response.json()
    if (response.status_code >= 500 or ("status_code" in data and data["status_code"] >= 500)):
        raise NicehashServerErrorException(response)
    elif(response.status_code >= 400 or ("status_code" in data and data["status_code"] >= 400)):
        raise NicehashAuthException(response)
    elif("error_code" in data and data["error_code"] > 0):
        raise NicehashClientErrorException(response)




def spin():

    # Load cookies
    cj = http.cookiejar.MozillaCookieJar(jar)
    cj.load(ignore_expires=True)
    #print(cj)

    headers = {
        'DNT': '1',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,nb;q=0.8,sv;q=0.7',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.52 Safari/537.36',
        'Accept': '*/*',
        'Referer': 'https://www.nicehash.com/wallet',
        'Connection': 'keep-alive',
    }

    params = (
        ('with', 'transactions,deposits,withdraws,withdraw_requests'),
    )
    #print(load_cookies(jar))
    cd = {c.name:c.value for c in cj}
    #print({c.name:c.value for c in cj})
    #return
    response = requests.get('https://www.nicehash.com/siteapi/user/wallet', headers=headers, params=params, cookies=cd)

    verifyResponse(response)

    nh_balance = float(response.json()['confirmed'])
    logger.info("Nicehash confirmed balance: %f mBTC", nh_balance*1000)

    # Make withdrawl to coinbase
    request_made = False
    if(nh_balance > 0.002):
        wd_headers = {
            'Origin': 'https://www.nicehash.com',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,nb;q=0.8,sv;q=0.7',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.52 Safari/537.36',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Referer': 'https://www.nicehash.com/wallet',
            'Connection': 'keep-alive',
            'DNT': '1',
        }


        wd_data = '{"address":"'+coinbase_account+'","amount":"'+str(nh_balance)+'","type":1}'
        logger.debug("Making withdrawl with data: %s", wd_data)
        logger.info("Transferring %f BTC, to coinbase account: %s", nh_balance, coinbase_account)
        wd_resp = requests.post('https://www.nicehash.com/siteapi/wallet/withdraw_create', headers=wd_headers, cookies=cd, data=wd_data)
        
        logger.debug(wd_resp.text)
        # {"withdraw_request_id":733146}

        verifyResponse(wd_resp)

        request_made = True
        logger.info("Sleeping 25 sec to wait for email")
        time.sleep(25)

    # Try to confirm the withdrawal by reading the email
    if((request_made or len(response.json()['withdraw_requests'])) > 0 and gmail_username):
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

            withdrawal_id = response.json()['withdraw_requests'][0]["id"]

            # Confirm withdrawal
            cf_headers = {
                'Origin': 'https://www.nicehash.com',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9,nb;q=0.8,sv;q=0.7',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.52 Safari/537.36',
                'Content-Type': 'application/json',
                'Accept': '*/*',
                'Referer': 'https://www.nicehash.com/wallet',
                'Connection': 'keep-alive',
                'DNT': '1',
            }

            cf_data = '{"code":"'+key+'","id":"'+str(withdrawal_id)+'","twofa":""}'
            logger.debug("Confirming withdrawal with data: %s", cf_data)
            logger.info("Confirming withdrawal %i, to coinbase account: %s", withdrawal_id, coinbase_account)
            cf_resp = requests.post('https://www.nicehash.com/siteapi/wallet/withdraw_confirm', headers=cf_headers, cookies=cd, data=cf_data)
            
            logger.debug(cf_resp.text)
            
            verifyResponse(cf_resp)

            
if __name__ == "__main__":
    logger.info("Starting Nicehash auto withdraw for Coinbase account: %s", coinbase_account)
    while(True):
        try:
            spin()
        except NicehashAuthException as e:
            logger.error("Nicehash authentication error, quitting: %s", e)
            raise e
        except NicehashServerErrorException as e:
            logger.error("Nicehash server error, retrying: %s", e)
            
        logger.info("Sleeping for %i seconds", spin_wait)
        #break
        time.sleep(spin_wait)
