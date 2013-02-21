'''
Created on Feb 23, 2012
@author: vandana
'''
from urlexpander import expandURL
import json
import httplib2
import logging
import urllib
import config
import sys
import time

class LinkTweets:
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.bloghandlesfile = config.PROJECT_ROOT + 'data/twitterhandles_summ.txt'
    
    def gettweets(self):
        http = httplib2.Http()
        f = open(self.bloghandlesfile, 'r')
        for thandle in f:
            tweetfile = config.PROJECT_ROOT + 'data/' + thandle.strip() + '_tweets.data'
            query = "from:" + thandle
            for k in range(1, 16):
                searchurl = 'http://search.twitter.com/search.json?rpp=100&q={0}&page={1}&include_entities=true&result_type=mixed'.format(urllib.quote_plus(query), k)
                response, content = http.request(searchurl, 'GET', headers={'User-Agent':'BlogProject'})
                if response['status'] == '200':
                    f1 = open(tweetfile, 'a')
                    content = json.loads(content)
                    results = content['results']
                    for tweet in results:
                        print tweet
                        urls = tweet['entities']['urls']
                        if len(urls) > 0:
                            #expanded_url = j['expanded_url']
                            #expanded_url = expandURL(expanded_url)
                            f1.write(json.dumps(tweet) + '\n')
                    f1.close()
            time.sleep(50)
        f.close()

def main(argv=None):
    t = LinkTweets()
    t.gettweets()
    #test()

def test():
    http = httplib2.Http()
    query = "from:engadget"
    searchurl = 'http://search.twitter.com/search.json?rpp=100&q={0}&include_entities=true&result_type=mixed'.format(urllib.quote_plus(query))
    response, content = http.request(searchurl, 'GET')
    f = open('/host/Users/vandana/Documents/Grad_Studies/Spring2012/IR/Project/data/engadget_tweets1', 'w')
    content = json.loads(content)
    results = content['results']
    for tweet in results:
        f.write(str(tweet) + '\n')
    
if __name__ == "__main__":
    sys.exit(main())

"""
f = open('/host/Users/vandana/Documents/Grad_Studies/Spring2012/IR/Project/data/techcrunch_tweets', 'r')
f1 = open('/host/Users/vandana/Documents/Grad_Studies/Spring2012/IR/Project/data/xxxx', 'w')

#datum = pickle.load(f)
expanded_url = ''
datum = f.readline()
print datum
datas = json.loads(datum)
result = datas["results"]
for i in result:
    entities = i['entities']
    urls = entities['urls']
    for j in urls:
        expanded_url = j['expanded_url']
    text = i['text']
    content = expandURL(expanded_url)
    if not content:
        logger.warning("Content not available from LongURL:%s" % expanded_url)
        continue
    expanded_url = content['long-url']
    title = None
    meta = None
    if 'title' in content:
        title = content['title']
    if 'meta-description' in content:
        meta = content['meta-description']
    print expanded_url
    Crawler.crawl(expanded_url, title, meta)
    #f1.write(c.html.body)
    #f1.write('----------------------------')
    #print c.html.body
    #print text

f.close()
f1.close()
"""