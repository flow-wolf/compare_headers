# Requirements:
#   1.) install requests module as shown below:
#       $ sudo -H pip install requests
import sys
import json
import requests
from collections import defaultdict


# define URLs to test
cf_url = 'http://flow-wolf.org/'
origin_url = 'http://88.98.197.254/'
urls_to_test =  { 'cloudflare': cf_url, 'origin': origin_url }


# function to perform HTTP GET
def get_url(url,timeout):
    try:
        r = requests.get(url,timeout=timeout)
    except requests.exceptions.RequestException as e:
        print (e)
        sys.exit(1)
    status_code = r.status_code
    resp_headers = r.headers
    return (status_code,dict(resp_headers))


# loop through list of URLs and extract headers + resp code and save results
recursivedict = lambda: defaultdict(recursivedict)
results = recursivedict()
for url in urls_to_test:
    status_code,resp_headers = get_url(urls_to_test[url],5)
    if status_code != 200:
        print ("status code for {0}: {1}, exiting script".format(url,status_code))
        sys.exit(1)
    else:
        results[url]['response code'] = status_code
        results[url]['response headers'] = resp_headers
print (json.dumps(results,indent=4,sort_keys=True))
