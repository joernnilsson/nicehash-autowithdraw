import requests, time, os, sys
import logging



class Client:


    def __init__(self, cookies):
        self.cookies = cookies

        self.headers = {
            'DNT': '1',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,nb;q=0.8,sv;q=0.7',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.52 Safari/537.36',
            'Accept': '*/*',
            'Referer': 'https://www.nicehash.com/wallet',
            'Connection': 'keep-alive',
        }

        self.logger = logging.getLogger()

    def wallet(self):
        
        params = (
            ('with', 'transactions,deposits,withdraws,withdraw_requests'),
        )
        return self.get('https://www.nicehash.com/siteapi/user/wallet', params=params)

    def withdrawal_request(self, coinbase_account, amount):

        data = '{"address":"'+coinbase_account+'","amount":"'+str(amount)+'","type":1}'
        return self.post('https://www.nicehash.com/siteapi/wallet/withdraw_create', data=data)

    def withdrawal_confirm(self, withdraw_request_id, key1, key2):

        data = '{"code":"'+key1+'-'+key2+'","id":"'+str(withdraw_request_id)+'","twofa":""}'
        return self.post('https://www.nicehash.com/siteapi/wallet/withdraw_confirm', data=data)


    def get(self, uri, params = None):
        self.logger.debug("GET: %s with params %s", uri, params)
        response = requests.get(uri, headers=self.headers, params=params, cookies=self.cookies)
        self.logger.debug("GET response(%i): %s", response.status_code, response.text)
        self.verifyResponse(response)
        
        return response.json()


    def post(self, uri, params = None, data = ""):
        self.logger.debug("POST: %s with params %s, data: %s", uri, params, data)
        response = requests.post(uri, headers=self.headers, params=params, cookies=self.cookies, data=data)
        self.logger.debug("POST response(%i): %s", response.status_code, response.text)
        self.verifyResponse(response)
        
        return response.json()
        
    def verifyResponse(self, response):
        if (response.status_code >= 500):
            raise NicehashServerErrorException(response)
        elif(response.status_code >= 400):
            raise NicehashAuthException(response)

        data = response.json()
        if ("status_code" in data and data["status_code"] >= 500):
            raise NicehashServerErrorException(response)
        elif("status_code" in data and data["status_code"] >= 400):
            raise NicehashAuthException(response)
        elif("error_code" in data and int(data["error_code"]) != 0):
            raise NicehashClientErrorException(response)
        elif("error" in data and int(data["error"]) != 0):
            raise NicehashServerErrorException(response)

class NicehashException(Exception):
    def __init__(self, response):
        self.response = response
        self.status_code = response.status_code
    def __str__(self):
        return 'NicehashException: %s %s' % (str(self.status_code), self.response.text)

class NicehashAuthException(NicehashException): pass
class NicehashServerErrorException(NicehashException): pass
class NicehashClientErrorException(NicehashException): pass
class NicehashUnknownErrorException(NicehashException): pass



