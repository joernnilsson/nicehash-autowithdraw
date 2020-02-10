[![Docker Build Status](https://img.shields.io/docker/build/joernsn/nicehash-autowithdraw.svg?style=flat-square)]()

# Nicehash Auto Withdraw to Coinbase
Automatically withdraws BTC funds from your Nicehash wallet to a Coinbase account


### Usage


```
usage: nicehash_auto_withdraw.py [-h] [--coinbase-account COINBASE_ACCOUNT]
                                 [--nicehash-organization NICEHASH_ORGANIZATION]
                                 [--nicehash-api-key NICEHASH_API_KEY]
                                 [--nicehash-api-secret NICEHASH_API_SECRET]

Withdraw BTC funds to Coinbase account

optional arguments:
  -h, --help            show this help message and exit
  --coinbase-account COINBASE_ACCOUNT, -c COINBASE_ACCOUNT
                        Coinbase account email address [COINBASE_ACCOUNT]
  --nicehash-organization NICEHASH_ORGANIZATION, -o NICEHASH_ORGANIZATION
                        Nicehash organization id [NICEHASH_ORGANIZATION]
  --nicehash-api-key NICEHASH_API_KEY, -k NICEHASH_API_KEY
                        Nicehash API key [NICEHASH_API_KEY]
  --nicehash-api-secret NICEHASH_API_SECRET, -s NICEHASH_API_SECRET
                        Nicehash API secret [NICEHASH_API_SECRET]

```

Where the email address is the target coinbase account. Email address can also be set as environment variable:
	
	COINBASE_ACCOUNT=email@gmail.com NICEHASH_ORGANIZATION=... NICEHASH_API_KEY=... NICEHASH_API_SECRET=... python3 nicehash_auto_withdraw.py 

### Docker

	docker pull joernsn/nicehash-autowithdraw
	docker run -it -d -e COINBASE_ACCOUNT=email@gmail.com -e NICEHASH_ORGANIZATION=... -e NICEHASH_API_KEY=... -e NICEHASH_API_SECRET=...  --name nh-auto joernsn/nicehash-autowithdraw
