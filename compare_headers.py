import sys
import json
import requests
import importlib
from collections import defaultdict


# start script
print ("\n\nSTART")


# 1.) define URLs to test
cf_url = 'http://flow-wolf.org/'
origin_url = 'http://88.98.197.254/'
urls_to_test =  { 'cloudflare': cf_url, 'origin': origin_url }


# 2.) function to perform HTTP GET
def get_url(url,timeout):
    try:
        r = requests.get(url,timeout=timeout)
    except requests.exceptions.RequestException as e:
        print (e)
        sys.exit(1)
    status_code = r.status_code
    resp_headers = r.headers
    return (status_code,dict(resp_headers))


# 3.) for each URL, extract resp headers + resp code, and save to dictionary
print ("\n\nHTTP GET response:")
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
        results[url]['url'] = urls_to_test[url]
print (json.dumps(results,indent=4,sort_keys=True))


# 4.) find the difference between both response headers
cf_headers = results['cloudflare']['response headers']
or_headers = results['origin']['response headers']
output = list()
for header in or_headers:
    if not header in cf_headers:
        output.append("origin header \"{0}\" missing from cloudflare response headers ".format(header))
    elif or_headers[header] != cf_headers[header]:
        output.append("origin [{0} : {1}] != cloudflare [{0} : {2}]".format(header,or_headers[header],cf_headers[header]))
for header in cf_headers:
    if not header in or_headers:
        output.append("cloudflare header \"{0}\" missing from origin response headers ".format(header))
print ("\n\nDifferences between both response headers total {0}: ".format(len(output)))
for entry in output:
    print ("{0}{1}{2}".format(output.index(entry)+1,'.) ',entry))


# end of script
print("\n\nFIN\n\n")
