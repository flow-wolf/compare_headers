#!/usr/bin/env python
#title           :compare_headers.py
#description     :copares headers between reverse proxy and origin
#author          :JRY
#date            :20171111
#version         :0.2
#usage           :python compare_headers.py
#notes           :
#python_version  :2.6
#requirements    :requests (sudo -H pip install requests)
#==============================================================================
import re
import sys
import json
import getopt
import requests
from collections import defaultdict


# define usage
usage = '''

usaage: python compare_headers.py -c <cdn domain> -o <origin domain>
    -c             cdn domain name or IP, required
    -o             origin domain name or IP, required
    -p             path, ie. /index.html, default is /
    -t             timeout in seconds, default is 5 seconds
    --cheaders     cdn headers in JSON format, optional
    --oheaders     origin headers in JSON format, optionals

'''


def is_valid_hostname(hostname):
    matchObj = re.match( r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$', hostname, re.M|re.I)
    if len(hostname) > 255:
        return False
    if matchObj:
        return True


# get options
def main(argv):
    origin = ''
    cdn = ''
    relative_path = '/'
    timeout = 5
    origin_headers = ''
    cdn_headers = ''
    try:
        opts, args = getopt.getopt(argv,"p:o:c:t:",["originheaders=","cdnheaders=""help"])
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
        elif opt == ("--originheaders"):
            origin_headers = arg
        elif opt == ("--cdnheaders"):
            cdn_headers = arg
        else:
            print (usage)
            sys.exit()
    if origin == False or cdn == False:
        print (usage)
        sys.exit()
    return (cdn,origin,relative_path,timeout,origin_headers,cdn_headers)


cdn,origin,relative_path,timeout,origin_headers,cdn_headers = main(sys.argv[1:])
if not relative_path.startswith("/"):
    relative_path = '/'+relative_path
print ('timeout is: {0} sec'.format(timeout))
print ('relative path is: {0}'.format(relative_path))
print ('origin is: {0}'.format(origin))
print ('cdn is: {0}'.format(cdn))
print ('origin headers are: {0}'.format(origin_headers))
print ('cdn headers are: {0}'.format(cdn_headers))


#1.) define URLs to test
cdn_url = 'http://' + cdn + relative_path
origin_url = 'http://' + origin + relative_path
urls_to_test =  { 'cdn': cdn_url, 'origin': origin_url }


#2.) function to perform HTTP GET
def get_url(url,timeout):
    try:
        r = requests.get(url,timeout=timeout,allow_redirects=False)
    except requests.exceptions.RequestException as e:
        print (e)
        sys.exit(1)
    status_code = r.status_code
    resp_headers = r.headers
    return (status_code,dict(resp_headers))


#3.) for each URL, extract resp headers + resp code, and save to dictionary
print ("\n\nHTTP GET response:")
recursivedict = lambda: defaultdict(recursivedict)
results = recursivedict()
for url in urls_to_test:
    status_code,resp_headers = get_url(urls_to_test[url],int(timeout))
    if (str(status_code)[:1]) != '2' and (str(status_code)[:1]) != '3' and (str(status_code)[:1]) != '4':
        print ("status code for {0}: {1}, exiting script\n".format(urls_to_test[url],status_code))
        sys.exit(1)
    else:
        results[url]['response code'] = status_code
        results[url]['response headers'] = resp_headers
        results[url]['url'] = urls_to_test[url]
results['timeout'] = timeout


#4.) find the difference between both response headers
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
