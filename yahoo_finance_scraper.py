import re
import json
import time
import random
import datetime
import requests
import xmltodict
from requests.exceptions import HTTPError
import pandas as pd
import multiprocessing
import undetected_chromedriver.v2 as uc
from pprint import pprint
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from scrape_proxies import get_random_proxy_csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

def browser():
    ua = UserAgent()
    user_agent = ua.random
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument(f"user-agent={user_agent}")
    driver = uc.Chrome(options=options, use_subprocess=True)
    return driver

def get_unix_timestamp(year, month, day, hour, minute, second):
    # Convert to unix datetime object
    date_time = datetime.datetime(year, month, day, hour, minute, second)

    print(date_time)

    # Get unix timestamp as an integer
    unix_timestamp = int((time.mktime(date_time.timetuple())))

    print(unix_timestamp)

    return unix_timestamp

def get_soup(url, headers, proxies):
    # Get response
    response = requests.get(url, headers=headers, proxies=proxies)

    # Initialize soup object
    soup = BeautifulSoup(response.content, "html.parser")

    #print(soup.prettify())

    # Return soup object
    return soup

def scrape_options_data(symbol):
    print("Scraping options data for: {}".format(symbol))

    url = "https://finance.yahoo.com/quote/{}/options?p={}".format(symbol, symbol)

    # Get random user agent
    ua = UserAgent()
    user_agent = ua.random

    headers = {
        'User-Agent': user_agent,
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://finance.yahoo.com/quote/TSLA/options?p=TSLA',
        'Origin': 'https://finance.yahoo.com',
        'Connection': 'keep-alive',
        # Requests sorts cookies= alphabetically
        # 'Cookie': 'A3=d=AQABBLX2XGICEIip4lvNRXxNsmZ-15nWfsAFEgEABgLXYGI6Y9wazSMA_eMBAAcItfZcYpnWfsAID8PHatmZCbS4Gbo92E9nYwkBBwoBcw&S=AQAAApl7A6zky5sTUBH20VHsJXk; B=c0vmmj5h5ptll&b=4&d=nW7xH6dtYFrr0fb3zsRc&s=c4&i=w8dq2ZkJtLgZuj3YT2dj; GUC=AQEABgJiYNdjOkIhGQTc; A1=d=AQABBLX2XGICEIip4lvNRXxNsmZ-15nWfsAFEgEABgLXYGI6Y9wazSMA_eMBAAcItfZcYpnWfsAID8PHatmZCbS4Gbo92E9nYwkBBwoBcw&S=AQAAApl7A6zky5sTUBH20VHsJXk; cmp=t=1657242132&j=0&u=1---; OTH=v=1&d=eyJraWQiOiIwMTY0MGY5MDNhMjRlMWMxZjA5N2ViZGEyZDA5YjE5NmM5ZGUzZWQ5IiwiYWxnIjoiUlMyNTYifQ.eyJjdSI6eyJndWlkIjoiNkVVTVNJSVA1WkVQWUxTVklBM1JCV05GVlkiLCJwZXJzaXN0ZW50Ijp0cnVlLCJzaWQiOiJpN213cXc1QzdxVEgifX0.Iw4UfU8_y1rsgrRHoIdPwecBtdaQQE51bvgTFf77xFDyJ_lSEGjIKBkgJ083DGZzHrSsBs9f9lUA5e0Pm4fN9T03R7lIcu4SkM6B79f7gCctkezC4W8WsqLuA8px5z-UYxdo3_-YBRPSNevcyY05j08IIsfAGx1eB76YYsRd5ko; T=af=QkNBQkJBJnRzPTE2NTcwNzI2MjYmcHM9RDZVelNzbjlHVFhkYUlhSzZFQmREZy0t&d=bnMBeWFob28BZwE2RVVNU0lJUDVaRVBZTFNWSUEzUkJXTkZWWQFhYwFBRlVSdHQ3RQFhbAFyYWtlc2guYmhhdGlhMQFzYwFkZXNrdG9wX3dlYgFmcwFhY3JmZS5WaVg0aXEBenoBWHUxdWlCT2VIAWEBUUFFAWxhdAFQazRYaUIBbnUBMAF0ZgFCQUE-&kt=EAAAQnwwSIfrHQxRNaNLM4HFA--~I&ku=FAAsLW6eFQdN4E9OHfAG7FAyugrjMoWuUbsg8NP1D_E1wdxw0a4oy0xf9kLdk1JyKtb1azBJFbosaM0Xt0xiTT7h0lSTypCrMFpnZSPx47G.im3ngo6Emdk2uGdu6XuDpeukRo8iLywORK6NpwfiTfj2m6qryKlfIDZmDMPbuZxEF4-~E; F=d=2gV8Cus9vxPJ.uZbRWUIkA9OPON19sEYsrQR9rigSxTgn6qDh0i.9mjSCrhpGrmSXYUGwutcsfQ-; PH=l=en-US; Y=v=1&n=515jccgd3m6ov&l=h0a4i7.170j80r/o&p=m2nvvvv00000000&r=vd&intl=us; ucs=tr=1657159026000; PRF=t%3DTSLA%252BAAPL%252BNVDA%252B%255EDJI%252B%255EGSPC%252BCRM%252B%255EIXIC%252BACAS%252BAPCX%252BAPC.F%252BFOXA%252BHBI%252BJETS%252BGREK%252BAMC; A1S=d=AQABBLX2XGICEIip4lvNRXxNsmZ-15nWfsAFEgEABgLXYGI6Y9wazSMA_eMBAAcItfZcYpnWfsAID8PHatmZCbS4Gbo92E9nYwkBBwoBcw&S=AQAAApl7A6zky5sTUBH20VHsJXk&j=WORLD',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
    }

    #proxies = {"http": "http://150.230.104.199:9090", "https": "http://150.230.104.199:9090"}
    proxies = None

    soup = get_soup(url, headers, proxies)

    script = soup.find("script", text=re.compile("root.App.main")).text
    data = json.loads(re.search("root.App.main\\s+=\\s+(\\{.*\\})", script).group(1))

    stores = data["context"]["dispatcher"]["stores"]

    #print(stores)

    #with open("stores.json", "w") as js:
    #    js.write(str(stores))

    #with open("stores.json", "w") as out:
    #    out.write(json.dumps(stores, indent = 4, sort_keys=True))
        #print(json.dumps(stores, indent = 4, sort_keys=True))
        #pprint(str(stores), stream=out)

    financial_data = stores["OptionContractsStore"]["contracts"]["calls"]
    
    print(json.dumps(financial_data, indent = 4, sort_keys=True))

    #with open("options_data.json", "w") as out:
    #    out.write(json.dumps(financial_data, indent = 4, sort_keys=True))
    
    #df = pd.DataFrame.from_dict(financial_data)
    
    df = pd.json_normalize(financial_data, max_level=1)
    print(df.head())

    df.to_csv("options-data-{}.csv".format(symbol))

    #pprint(financial_data)

    #options_data = stores["contracts"]["calls"]

    #print(options_data)

def get_options_data(symbol, time_tuple):
    print("Scraping options data for: {}".format(symbol))

    url = "https://finance.yahoo.com/quote/{}/options?p={}".format(symbol, symbol)

    # Get random user agent
    ua = UserAgent()
    user_agent = ua.random

    '''headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://finance.yahoo.com/quote/{}/options?p={}'.format(symbol, symbol),
        'Origin': 'https://finance.yahoo.com',
        'Connection': 'keep-alive',
        # Requests sorts cookies= alphabetically
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
    }'''

    cookies = {
        'A3': 'd=AQABBLX2XGICEIip4lvNRXxNsmZ-15nWfsAFEgEABgLXYGI6Y9wazSMA_eMBAAcItfZcYpnWfsAID8PHatmZCbS4Gbo92E9nYwkBBwoBcw&S=AQAAApl7A6zky5sTUBH20VHsJXk',
        'B': 'c0vmmj5h5ptll&b=4&d=nW7xH6dtYFrr0fb3zsRc&s=c4&i=w8dq2ZkJtLgZuj3YT2dj',
        'GUC': 'AQEABgJiYNdjOkIhGQTc',
        'A1': 'd=AQABBLX2XGICEIip4lvNRXxNsmZ-15nWfsAFEgEABgLXYGI6Y9wazSMA_eMBAAcItfZcYpnWfsAID8PHatmZCbS4Gbo92E9nYwkBBwoBcw&S=AQAAApl7A6zky5sTUBH20VHsJXk',
        'cmp': 't=1657242132&j=0&u=1---',
        'OTH': 'v=1&d=eyJraWQiOiIwMTY0MGY5MDNhMjRlMWMxZjA5N2ViZGEyZDA5YjE5NmM5ZGUzZWQ5IiwiYWxnIjoiUlMyNTYifQ.eyJjdSI6eyJndWlkIjoiNkVVTVNJSVA1WkVQWUxTVklBM1JCV05GVlkiLCJwZXJzaXN0ZW50Ijp0cnVlLCJzaWQiOiJpN213cXc1QzdxVEgifX0.Iw4UfU8_y1rsgrRHoIdPwecBtdaQQE51bvgTFf77xFDyJ_lSEGjIKBkgJ083DGZzHrSsBs9f9lUA5e0Pm4fN9T03R7lIcu4SkM6B79f7gCctkezC4W8WsqLuA8px5z-UYxdo3_-YBRPSNevcyY05j08IIsfAGx1eB76YYsRd5ko',
        'T': 'af=QkNBQkJBJnRzPTE2NTcwNzI2MjYmcHM9RDZVelNzbjlHVFhkYUlhSzZFQmREZy0t&d=bnMBeWFob28BZwE2RVVNU0lJUDVaRVBZTFNWSUEzUkJXTkZWWQFhYwFBRlVSdHQ3RQFhbAFyYWtlc2guYmhhdGlhMQFzYwFkZXNrdG9wX3dlYgFmcwFhY3JmZS5WaVg0aXEBenoBWHUxdWlCT2VIAWEBUUFFAWxhdAFQazRYaUIBbnUBMAF0ZgFCQUE-&kt=EAAAQnwwSIfrHQxRNaNLM4HFA--~I&ku=FAAsLW6eFQdN4E9OHfAG7FAyugrjMoWuUbsg8NP1D_E1wdxw0a4oy0xf9kLdk1JyKtb1azBJFbosaM0Xt0xiTT7h0lSTypCrMFpnZSPx47G.im3ngo6Emdk2uGdu6XuDpeukRo8iLywORK6NpwfiTfj2m6qryKlfIDZmDMPbuZxEF4-~E',
        'F': 'd=2gV8Cus9vxPJ.uZbRWUIkA9OPON19sEYsrQR9rigSxTgn6qDh0i.9mjSCrhpGrmSXYUGwutcsfQ-',
        'PH': 'l=en-US',
        'Y': 'v=1&n=515jccgd3m6ov&l=h0a4i7.170j80r/o&p=m2nvvvv00000000&r=vd&intl=us',
        'ucs': 'tr=1657159026000',
        'PRF': f't%3DTSLA%252BAAPL%252BNVDA%252B%255EDJI%252B%255EGSPC%252BCRM%252B%255EIXIC%252BACAS%252BAPCX%252BAPC.F%252BFOXA%252BHBI%252BJETS%252BGREK%252BAMC',
        'A1S': 'd=AQABBLX2XGICEIip4lvNRXxNsmZ-15nWfsAFEgEABgLXYGI6Y9wazSMA_eMBAAcItfZcYpnWfsAID8PHatmZCbS4Gbo92E9nYwkBBwoBcw&S=AQAAApl7A6zky5sTUBH20VHsJXk&j=WORLD',
    }

    # Set headers
    '''headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Host': 'www.zillow.com',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'TE': 'trailers',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': user_agent
    }'''

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://finance.yahoo.com/quote/TSLA/options?p=TSLA',
        'Origin': 'https://finance.yahoo.com',
        'Connection': 'keep-alive',
        # Requests sorts cookies= alphabetically
        # 'Cookie': 'A3=d=AQABBLX2XGICEIip4lvNRXxNsmZ-15nWfsAFEgEABgLXYGI6Y9wazSMA_eMBAAcItfZcYpnWfsAID8PHatmZCbS4Gbo92E9nYwkBBwoBcw&S=AQAAApl7A6zky5sTUBH20VHsJXk; B=c0vmmj5h5ptll&b=4&d=nW7xH6dtYFrr0fb3zsRc&s=c4&i=w8dq2ZkJtLgZuj3YT2dj; GUC=AQEABgJiYNdjOkIhGQTc; A1=d=AQABBLX2XGICEIip4lvNRXxNsmZ-15nWfsAFEgEABgLXYGI6Y9wazSMA_eMBAAcItfZcYpnWfsAID8PHatmZCbS4Gbo92E9nYwkBBwoBcw&S=AQAAApl7A6zky5sTUBH20VHsJXk; cmp=t=1657242132&j=0&u=1---; OTH=v=1&d=eyJraWQiOiIwMTY0MGY5MDNhMjRlMWMxZjA5N2ViZGEyZDA5YjE5NmM5ZGUzZWQ5IiwiYWxnIjoiUlMyNTYifQ.eyJjdSI6eyJndWlkIjoiNkVVTVNJSVA1WkVQWUxTVklBM1JCV05GVlkiLCJwZXJzaXN0ZW50Ijp0cnVlLCJzaWQiOiJpN213cXc1QzdxVEgifX0.Iw4UfU8_y1rsgrRHoIdPwecBtdaQQE51bvgTFf77xFDyJ_lSEGjIKBkgJ083DGZzHrSsBs9f9lUA5e0Pm4fN9T03R7lIcu4SkM6B79f7gCctkezC4W8WsqLuA8px5z-UYxdo3_-YBRPSNevcyY05j08IIsfAGx1eB76YYsRd5ko; T=af=QkNBQkJBJnRzPTE2NTcwNzI2MjYmcHM9RDZVelNzbjlHVFhkYUlhSzZFQmREZy0t&d=bnMBeWFob28BZwE2RVVNU0lJUDVaRVBZTFNWSUEzUkJXTkZWWQFhYwFBRlVSdHQ3RQFhbAFyYWtlc2guYmhhdGlhMQFzYwFkZXNrdG9wX3dlYgFmcwFhY3JmZS5WaVg0aXEBenoBWHUxdWlCT2VIAWEBUUFFAWxhdAFQazRYaUIBbnUBMAF0ZgFCQUE-&kt=EAAAQnwwSIfrHQxRNaNLM4HFA--~I&ku=FAAsLW6eFQdN4E9OHfAG7FAyugrjMoWuUbsg8NP1D_E1wdxw0a4oy0xf9kLdk1JyKtb1azBJFbosaM0Xt0xiTT7h0lSTypCrMFpnZSPx47G.im3ngo6Emdk2uGdu6XuDpeukRo8iLywORK6NpwfiTfj2m6qryKlfIDZmDMPbuZxEF4-~E; F=d=2gV8Cus9vxPJ.uZbRWUIkA9OPON19sEYsrQR9rigSxTgn6qDh0i.9mjSCrhpGrmSXYUGwutcsfQ-; PH=l=en-US; Y=v=1&n=515jccgd3m6ov&l=h0a4i7.170j80r/o&p=m2nvvvv00000000&r=vd&intl=us; ucs=tr=1657159026000; PRF=t%3DTSLA%252BAAPL%252BNVDA%252B%255EDJI%252B%255EGSPC%252BCRM%252B%255EIXIC%252BACAS%252BAPCX%252BAPC.F%252BFOXA%252BHBI%252BJETS%252BGREK%252BAMC; A1S=d=AQABBLX2XGICEIip4lvNRXxNsmZ-15nWfsAFEgEABgLXYGI6Y9wazSMA_eMBAAcItfZcYpnWfsAID8PHatmZCbS4Gbo92E9nYwkBBwoBcw&S=AQAAApl7A6zky5sTUBH20VHsJXk&j=WORLD',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
    }

    # Set proxies
    proxies = {"http": "http://150.230.104.199:9090", "https": "http://150.230.104.199:9090"}

    # Get datetime for yahoo finance params payload
    unix_timestamp = get_unix_timestamp(time_tuple[0], time_tuple[1], time_tuple[2], time_tuple[3], time_tuple[4], time_tuple[5])

    # Set params
    params = {
        'formatted': 'true',
        'crumb': 'N4v6f8SXQ/X',
        'lang': 'en-US',
        'region': 'US',
        'date': unix_timestamp,
        'corsDomain': 'finance.yahoo.com',
    }

    response = requests.get(url, params=params, cookies=cookies, headers=headers)
    response.raise_for_status()
    with open("response.xml", "w") as xml_file:
        xml_file.write(response.text)
        xml_file.close()

    '''try:
        #response = requests.get(url, headers=headers, proxies=proxies, params=params)
        response = requests.get(url, params=params, cookies=cookies, headers=headers)
        response.raise_for_status()
        data = xmltodict.parse(response.text)
        json_data = json.dumps(data)
        print("Entire JSON response")
        print(json_data)
        #print(response.text)
        #print(response.headers['Content-Type'])
        # access JSON content
        #jsonResponse = response.json()
        #jsonResponse = json.loads(response.json(), encoding='utf-8')
        #jsonResponse = json.loads(response.text)
        #print("Entire JSON response")
        #print(jsonResponse)
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")'''

    #soup = get_soup(url, headers, proxies, params)

    #print(response.json())

    #return response.json()

def main():
    start = time.time()

    # Yahoo sets time of expiration for options at 5pm the prior day
    #unix_timestamp = get_unix_timestamp(2022, 7, 7, 17, 0, 0)

    symbol = "TSLA"

    #time_tuple = (2022, 7, 7, 17, 0, 0)

    #get_options_data(symbol, time_tuple)

    scrape_options_data(symbol)

    end = time.time()
    execution_time = end - start
    print("Execution time: {} seconds".format(execution_time))

if __name__ == "__main__":
    main()
