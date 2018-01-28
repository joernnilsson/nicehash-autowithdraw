# Nicehash Auto Withdraw to Coinbase
Automatically withdraws BTC funds from your Nicehash wallet to a Coinbase account


### Auth
The script needs a cookie from Nicehash for authentication. Log into Nicehash and user the [cookie.txt](https://chrome.google.com/webstore/detail/cookiestxt/njabckikapfpffapmjgojcnbfjonfjfg?hl=en) extension for Chrome to save cookie.txt to the data folder.

### Run
	COINBASE_ACCOUNT=coinbase-emai@address.com python3 auto-withdraw.py
	
### Docker
	docker build -t nicehash-autowithdraw .; docker run -v $(pwd)/data:/data -it -d -e COINBASE_ACCOUNT=coinbase-emai@address.com --name nh-auto  nicehash-autowithdraw