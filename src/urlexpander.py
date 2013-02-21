import httplib2
import urllib
import pickle
import json
import config
from utilities.mpycache import LRUCache

CACHE_MAX_SIZE = 0 #can restrict later
CACHE_MAX_AGE = 0 #can restrict later, enter time in millisecs
CACHE_FILE = config.PROJECT_ROOT + 'cache'
f = open(CACHE_FILE, 'w')
lrucache = LRUCache(CACHE_MAX_SIZE, CACHE_MAX_AGE)
pickle.dump(lrucache, f)
f.close()

def createRequest(tweeturl):
    turl = urllib.quote_plus(tweeturl)
    url = 'http://api.longurl.org/v2/expand?url={0}&all-redirects=1&content-type=1&response-code=1&title=1&meta-keywords=1&meta-description=1&format=json'.format(turl)
    return url

def expandURL(tweeturl):
    http = httplib2.Http()
    f1 = open(CACHE_FILE, 'r+')
    lrucache = pickle.load(f1)
    ua = 'TweetUrlVB/1.0'
    if lrucache.has_key(tweeturl):
        return lrucache.get(tweeturl)
    url = createRequest(tweeturl)
    response, content = http.request(url, 'GET', headers={'User-Agent':ua})
    #print response
    #print content
    if response['status'] == '200':
        lrucache.put(tweeturl, content)
        pickle.dump(lrucache, f1)
        content = json.loads(content)
    else:
        content = json.loads(content)
        content['long-url'] = tweeturl
    return content
    