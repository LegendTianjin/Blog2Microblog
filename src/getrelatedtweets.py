'''
Created on Feb 28, 2012
@author: vandana
'''
import httplib2
import urllib
import re
import json
import config
import sys
import os
import time
from pymongo import Connection
from nltk.corpus import stopwords

class RelatedTweets:
    
    def __init__(self, path):
        self.linkspath = path
        dbConn = Connection("localhost", 27017)
        self.db = dbConn.b2mb
        self.db.tweets.ensure_index('id_str', unique=True)
        
    def gettweets(self):
        for (root, dirs, files) in os.walk(self.linkspath):
            for file_t in files:
                if '.data' in file_t:
                    domain = file_t.split('_')[0]
                    
                    f = open(os.path.join(root, file_t), 'r')
                    c = 0
                    for line in f:
                        c += 1
                        line = json.loads(line)
                        self.getrelatedtweets(line, domain)
                        #will get tweets for max 400 link tweets per domain for now
                        
                        if c > 400:
                            break
                        
    
    def getrelatedtweets(self, tweet, th):
        http = httplib2.Http()
        idstr = tweet['id_str']
        print idstr, " ", th
        url = tweet['entities']['urls'][0]['url']
        tweet['related_tweet'] = idstr
        tweet['url'] = url
        it = self.db.tweet.find({'id_str':tweet['id_str']})
        for i in it:
            return
        self.db.tweets.insert(tweet)
        text = tweet['text'].lower()
        to_user_id = tweet['from_user']
        text = re.sub(r'(@\w+)|(http://.*)|(#\w+)|(\d+)', "", text)
        words = re.findall(r'\w+', text, flags = re.UNICODE | re.LOCALE)
        imp_words = filter(lambda x:x not in stopwords.words('english'), words)
        imp_words = ' '.join(imp_words)
        q = [imp_words, 'to:'+to_user_id, '#'+to_user_id]
        #f = open(self.linkspath+"alltweets.txt", 'w')
        for i in range(len(q)):
            for k in range(1, 16):
                searchurl = 'http://search.twitter.com/search.json?rpp=100&q={0}&page={1}&include_entities=true&result_type=mixed'.format(urllib.quote_plus(q[i]), k)
                response, content = http.request(searchurl, 'GET')
                if response['status'] == '200':
                    #check if tweet is in response to the particular tweet id or contains all the words? is not a retweet.
                    #in_reply_to_status_id_str, or contains all or some important keywords (especially the first 2-3 words
                    content = json.loads(content)
                    results = content['results']
                    if len(results) == 0:
                        break
                    twts = []
                    for twt in results:
                        if (i == 0 and 'RT' not in twt['text']) or ('in_reply_to_status_id_str' in twt and twt['in_reply_to_status_id_str'] == idstr):
                            twt['related_tweet'] = idstr
                            twts.append(twt)
                            #print twt
                            #f.write(str(twt)+'\n')
                    if len(twts) > 0:
                        self.db.tweets.insert(twts)
                elif response['status'] == '420':
                    print response
                    time.sleep(int(response['retry-after']))
            time.sleep(30)
            #f.write('\n-----------\n')
        #f.close()

def main(argv=None):    
    t = RelatedTweets(config.PROJECT_ROOT + "data/")
    t.gettweets()

if __name__ == '__main__':
    sys.exit(main())