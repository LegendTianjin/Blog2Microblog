'''
Created on Apr 4, 2012
@author: vandana
This is the entry point into the python Blog2Microblog modules from the web-based tool.
'''

import re
import ratingslearner
import crawler
import util
import json
import urllib
import sys
import httplib2
from recommendersystem import Recommender
from pymongo import Connection
from urlexpander import expandURL
from nltk.corpus import stopwords

class RequestPipeline:
    def __init__(self, url):
        self.url = url
        self.items = []
        self.tweets = []
        dbConn = Connection("localhost", 27017)
        self.db = dbConn.b2mb
        self.lambda1 = 1.0
        self.indb = 1
    
    def processrequest(self):
        domain = ""
        if re.search(r'(eng*\.co)|(engadget\.com.*)', self.url) != None:
            domain = 'engadget'
        elif re.search(r'(mash*\.to)|(mashable\.*)', self.url) != None:
            domain = 'mashable'
        elif re.search(r'ndtv', self.url) != None:
            domain = 'ndtv'
        elif re.search(r'fakingnews', self.url) != None:
            domain = 'fakingnews'
        elif re.search(r'treehugger', self.url) != None or 'treehugger' in expandURL(self.url)['long-url']:
            domain = 'treehugger'
        elif re.search(r'news\.cnet', self.url) != None:
            domain = 'cnetnews'
        if domain == "":
            return self.geterrorresponse("Url Not Valid...")
        
        self.domain = domain
        bh = crawler.BlogHtml(self.url, domain)
        self.title = bh.title
        self.items = util.getitems(bh.title, bh.blogparas)
    
    def setlambda(self, l):
        self.lambda1 = l
    
    def getrateditems(self):
        response = ratingslearner.predictratings(self.items)
        response = json.loads(response)
        if response == None or response['status'] == 400:
            return []
        items = response['content']
        ''' Debugging '''
        """
        for i in items:
            print i['text'], i['rating'], i['position']
        """
        return items
    
    def processrequest_gettweets(self):
        tweets = []
        punctpattern = re.compile(r'[,;\'"\)\(}{\[\].!\?<>=+-/*\\:]+')
        http = httplib2.Http()
        """
        tokens = util.tokenize(self.title)
        qts = []
        for i in tokens:
            #if i in stopwords.words('english') or punctpattern.match(i) != None:
            if punctpattern.match(i) != None:
                continue
            qts.append(i)
        twords = ' '.join(qts)
        q = twords + ' from:' + self.domain
        """
        q = self.title + ' from:' + self.domain
        searchurl = 'http://search.twitter.com/search.json?rpp=100&q={0}&page=1&include_entities=true&result_type=mixed'.format(urllib.quote_plus(q))
        response, content = http.request(searchurl, 'GET')
        if response['status'] == '200':
            content = json.loads(content)
            results = content['results']
            if len(results) > 0:
                tweet = results[0]
                tweetsjsonarr = []
                idstr = tweet['id_str']
                to_user_id = tweet['from_user']
                q = 'to:'+to_user_id + ' OR ' + '#'+to_user_id
                for k in range(1, 16):
                    searchurl = 'http://search.twitter.com/search.json?rpp=100&q={0}&page={1}&include_entities=true&result_type=mixed'.format(urllib.quote_plus(q), k)
                    response, content = http.request(searchurl, 'GET')
                    if response['status'] == '200':
                        content = json.loads(content)
                        results = content['results']
                        if len(results) == 0:
                            break
                        twts = []
                        for twt in results:
                            if 'in_reply_to_status_id_str' in twt and twt['in_reply_to_status_id_str'] == idstr:
                                twt['related_tweet'] = idstr
                                twts.append(twt)
                        if len(twts) > 0:
                            tweetsjsonarr.extend(twts)
                if len(tweetsjsonarr) > 0:
                    tweets = util.gettweets(tweetsjsonarr, self.items, self.title)
        #self.tweets = tweets
        return tweets
    
    def getrecommenderbasedresponse(self):
        response = {}
        r = Recommender(self.lambda1)
        r.creatematrix(self.items, self.tweets)
        r.calcaggregateratings()
        items = r.getrecommenderrateditems()
        if items == []:
            return self.geterrorresponse("Items could not be rated as per the recommender system")
        else:
            (summary, tweettext) = self.getsummary(items)
            blogcontent = [i.content for i in self.items]
            (infogain1, infogain2) = util.informationgaincompare(" ".join(blogcontent), tweettext, self.title)
            response['status'] = 200
            response['content'] = {'summary':summary, 'tweettext':tweettext, 'tweettextinfogain':infogain1, 'titleinfogain':infogain2}
            response['title'] = self.title
            return json.dumps(response)
        return response
    
    def processrequest_gettweetsfromdb(self):
        id_it = self.db.blogcontent.find({'url':self.url})
        c = 0
        for blog in id_it:
            c += 1
            break
        if c == 0:
            return []
        twt_it = self.db.tweets.find({'related_tweet':blog['id_str']})
        twts = [] 
        for i in twt_it:
            twts.append(i)
        if len(twts) == 0:
            return []
        tweets = util.gettweets(twts, self.items, self.title)
        #self.tweets = tweets
        return tweets

    def geterrorresponse(self, message):
        response = {}
        response['status'] = 400
        response['content'] = []
        response['message'] = message
        return json.dumps(response)
    
    def getresponse(self):
        response = {}
        items = self.getrateditems()
        if items == []:
            return self.geterrorresponse("Items could not be rated")
        else:
            (summary, tweettext) = self.getsummary(items)
            blogcontent = [i.content for i in self.items]
            (infogain1, infogain2) = util.informationgaincompare(" ".join(blogcontent), tweettext, self.title)
            response['status'] = 200
            response['content'] = {'summary':summary, 'tweettext':tweettext, 'tweettextinfogain':infogain1, 'titleinfogain':infogain2}
            response['title'] = self.title
            return json.dumps(response)
    
    def getsummary(self, items):
        sorted_items = sorted(items, key=lambda k: k['rating'], reverse=True)
        sorted_items = sorted_items[:5]
        sorted_items = sorted(sorted_items, key=lambda k: k['position'])
        tweettext = sorted_items[0]['text'][:140]
        return (sorted_items, tweettext)

def summarize(url=None, recommender='0', lambda1='1', indb='0'):
    #print recommender, lambda1
    url = urllib.unquote_plus(url)
    rp = RequestPipeline(url)
    rp.processrequest()
    isreco = int(recommender)
    if isreco:
        rp.setlambda(float(lambda1))
        if int(indb) == 1:
            rp.tweets = rp.processrequest_gettweetsfromdb()
        else:
            rp.tweets = rp.processrequest_gettweets()
        return rp.getrecommenderbasedresponse()
    else:
        return rp.getresponse()

def hello(url=None):
    return 'hello '+url

def main(argv=None):
    #encoded_url = urllib.quote_plus('http://www.treehugger.com/clean-technology/more-california-utilities-required-let-customers-opt-out-smart-meters.html')
    encoded_url = urllib.quote_plus('http://www.treehugger.com/clean-water/access-safe-water-and-sanitation-could-save-millions-annually.html')
    print encoded_url
    response = summarize(encoded_url, '1', '0.6', '0')
    response = json.loads(response)
    for i in response:
        print i, response[i]

if __name__ == "__main__":
    sys.exit(main())