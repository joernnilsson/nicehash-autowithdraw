[![Docker Build Status](https://img.shields.io/docker/build/joernsn/nicehash-autowithdraw.svg?style=flat-square)]()

# Nicehash Auto Withdraw to Coinbase
Automatically withdraws BTC funds from your Nicehash wallet to a Coinbase account


### Auth
The script needs a cookie from Nicehash for authentication. Log into Nicehash and use the [cookie.txt](https://chrome.google.com/webstore/detail/cookiestxt/njabckikapfpffapmjgojcnbfjonfjfg?hl=en) extension for Chrome to save cookie.txt to the data folder.

You will need to make one withdrawl manually first, to confirm the email address. Subsequent withdrawals will be confirmed automatically.

Tip: Grab the cookie from a chrome profile you do not use daily. It will be invalidated whenever you log out.


### Run


Run

	python3 nicehash_auto_withdraw.py email@gmail.com

Where the email address is the target coinbase account. Email address can also be set as environment variable:
	
	COINBASE_ACCOUNT=email@gmail.com python3 nicehash_auto_withdraw.py 

### Docker

	docker pull joernsn/nicehash-autowithdraw
	docker run -v $(pwd)/data:/data -it -d -e COINBASE_ACCOUNT=email@gmail.com --name nh-auto joernsn/nicehash-autowithdraw
