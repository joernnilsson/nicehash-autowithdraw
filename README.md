[![Docker Build Status](https://img.shields.io/docker/build/joernsn/nicehash-autowithdraw.svg?style=flat-square)]()

# Nicehash Auto Withdraw to Coinbase
Automatically withdraws BTC funds from your Nicehash wallet to a Coinbase account


### Auth
The script needs a cookie from Nicehash for authentication. Log into Nicehash and use the [cookie.txt](https://chrome.google.com/webstore/detail/cookiestxt/njabckikapfpffapmjgojcnbfjonfjfg?hl=en) extension for Chrome to save cookie.txt to the data folder.

Tip: Grab the cookie from a chrome profile you do not use daily. It will be invalidated whenever you log out.

The script expects these environment variables to be set:

	COINBASE_ACCOUNT=coinbase-email@address.com 
	GMAIL_USERNAME=your@gmail.com
	GMAIL_PASSWORD=yourpassword

### Run


Run

	python3 auto-withdraw.py
	
### Docker

	docker pull joernsn/nicehash-autowithdraw
	docker run -v $(pwd)/data:/data -it -d --env-file vars.env --name nh-auto joernsn/nicehash-autowithdraw
