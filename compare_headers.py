#!/usr/bin/env python
#title           :compare_headers.py
#description     :copares headers between reverse proxy and origin
#author          :JY
#date            :20171111
#version         :0.2
#usage           :python compare_headers.py
#notes           :
#python_version  :2.6 <
#requirements    :requests (sudo -H pip install requests)
#==============================================================================
import re
import sys
import json
import getopt
import requests
from collections import defaultdict


#1.) define usage
usage = '''

usaage: python compare_headers.py -c <cdn domain> -o <origin domain>
    -c             cdn domain name or IP, required arg
    -o             origin domain name or IP, required arg
    -p             path, ie. /index.html, default is /, optional
    -s             HTTPS, default is HTTP, optional
    -t             timeout in seconds, default is 5 seconds, optional
    --crh          cdn request headers in JSON format, optional
    --orh          origin request headers in JSON format, optional

'''


#2.) get options
def main(argv):
    origin = ''
    cdn = ''
    relative_path = '/'
    timeout = 5
    origin_headers = ''
    cdn_headers = ''
    scheme = 'HTTP'
    try:
        opts, args = getopt.getopt(argv,"p:o:c:t:s",["orh=","crh=","help"])
    except getopt.GetoptError:
        print (usage)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '--help':
            print (usage)
            sys.exit()
        elif opt in ("-p"):
            relative_path = arg
        elif opt in ("-o"):
            origin = arg
        elif opt in ("-c"):
            cdn = arg
        elif opt in ("-t"):
            timeout = arg
        elif opt == ("--orh"):
            try:
                origin_headers = json.loads(arg)
            except:
                text = "json syntax invalid or you forgot to put single quotes around your json: {}".format('\'{"Host":www.test.com,"User-Agent":"Mozilla"}\'')
                print ("\n{}\n".format(text))
                sys.exit()
        elif opt == ("--crh"):
            try:
                cdn_headers = json.loads(arg)
            except:
                text = "json syntax invalid or you forgot to put single quotes around your json: {}".format('\'{"Host":www.test.com,"User-Agent":"Mozilla"}\'')
                print ("\n{}\n".format(text))
                sys.exit()
        elif opt == ("-s"):
            scheme = 'HTTPS'
        else:
            print (usage)
            sys.exit()
    if origin == False or cdn == False:
        print (usage)
        sys.exit()
    return (cdn,origin,relative_path,timeout,origin_headers,cdn_headers,scheme)
cdn,origin,relative_path,timeout,origin_headers,cdn_headers,scheme = main(sys.argv[1:])


#3.) define URLs to test
cdn_url = scheme + '://' + cdn + relative_path
origin_url = scheme + '://' + origin + relative_path
urls_to_test =  { 'cdn': cdn_url, 'origin': origin_url }


#4.) function to perform HTTP GET
def get_url(url,timeout,request_headers):
    try:
        r = ''
        if not request_headers:
            r = requests.get(url,timeout=timeout,allow_redirects=False)
        else:
            r = requests.get(url,timeout=timeout,allow_redirects=False,headers=request_headers)
    except requests.exceptions.RequestException as e:
        print (e)
        print (usage)
        sys.exit(1)
    status_code = r.status_code
    resp_headers = r.headers
    return (status_code,dict(resp_headers))


#5.) for each URL, extract resp headers + resp code, and save to dictionary
print ("\n\nHTTP GET response:")
recursivedict = lambda: defaultdict(recursivedict)
results = recursivedict()
for url in urls_to_test:
    request_headers = dict()
    if url == 'cdn':
        request_headers = cdn_headers
    if url == 'origin':
        request_headers = origin_headers
    status_code,resp_headers = get_url(urls_to_test[url],int(timeout),request_headers)
    if (str(status_code)[:1]) != '2' and (str(status_code)[:1]) != '3' and (str(status_code)[:1]) != '4':
        print ("status code for {0}: {1}, exiting script\n".format(urls_to_test[url],status_code))
        sys.exit(1)
    else:
        results[url]['response code'] = status_code
        results[url]['response headers'] = resp_headers
        results[url]['url'] = urls_to_test[url]
results['timeout'] = timeout


#6.) find the difference between both response headers
cdn_headers = results['cdn']['response headers']
or_headers = results['origin']['response headers']
output = list()
for header in or_headers:
    if not header in cdn_headers:
        output.append("origin header [{0}] not in cdn headers ".format(header))
    elif or_headers[header] != cdn_headers[header]:
        output.append("origin [{0} : {1}] != cdn [{0} : {2}]".format(header,or_headers[header],cdn_headers[header]))
for header in cdn_headers:
    if not header in or_headers:
        output.append("cdn header [{0}] not in origin headers ".format(header))
for entry in output:
    results['differences'][output.index(entry)] = entry
print (json.dumps(results,indent=4,sort_keys=True))

# end script
