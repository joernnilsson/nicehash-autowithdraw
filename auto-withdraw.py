import requests, time, os, sys
import logging
import http.cookiejar

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


    #print(response.status_code)
    if(response.status_code != 200):
        logger.error("Nicehash returned status %i", response.status_code)
        raise Exception("Nicehash status not 200")

    #print(response.json())

    if('confirmed' not in response.json()):
        print(response.json())
        logger.error("Error getting confimed balance")
        raise Exception("Error getting confimed balance")
    

    nh_balance = float(response.json()['confirmed'])
    logger.info("Nicehash confirmed balance: %f mBTC", nh_balance*1000)

    # Make withdrawl to coinbase
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

        if(wd_resp.status_code != 200):
            logger.error("Nicehash withdraw returned status %i", wd_resp.status_code)
            logger.debug(wd_resp.text)
            raise Exception("Nicehash withdraw status not 200")

        if("error_code" in wd_resp.json()):
            error_code = int(wd_resp.json()['error_code'])
            error_messge = wd_resp.json()['error']
            logger.error("Nicehash withdraw error: %i, %s", error_code, error_messge)
            raise Exception("Nicehash withdraw error")

    #if(gmail_username):
        
    #    sleep(5)


if __name__ == "__main__":
    logger.info("Starting Nicehash auto withdraw for Coinbase account: %s", coinbase_account)
    while(True):
        spin()
        logger.info("Sleeping for %i seconds", spin_wait)
        #break
        time.sleep(spin_wait)