'''
Created on Mar 6, 2012
@author: vandana
'''
import sys
import operator
from math import log
import matplotlib.pyplot as plt
import pickle
from pymongo import Connection
import config
import os

class DataPatterns:
    def __init__(self):
        dbConn = Connection("localhost", 27017)
        self.db = dbConn.b2mb
    
    def findtweetdistrib(self):
        blogit = self.db.blogcontent.find()
        tweetdistrib = {}
        for i in blogit:
            tweetid = i['id_str']
            counttweet = self.db.tweets.find({'related_tweet' : tweetid}).count()
            print counttweet
            tweetdistrib[tweetid] = counttweet
        tweetdistrib_sorted = sorted(tweetdistrib.iteritems(), key=operator.itemgetter(1), reverse=True)
        self.tweetdistrib = tweetdistrib_sorted
        f = open("test", 'w')
        pickle.dump(self.tweetdistrib, f)
        print tweetdistrib_sorted
    
    
    def plottweetdistrib(self):
        #distrib = self.tweetdistrib
        f = open("test", 'r')
        distrib = pickle.load(f)
        (self.mostpopular, self.mostpopular_nt) = distrib[2]
        l = len(distrib)
        x = [0] * l
        y = [0] * l
        for i in range(l):
            if i > 0:
                x[i] = log(i)
            (p,q) = distrib[i]
            if q > 0:
                y[i] = log(q)
        plt.plot(x, y, color='green', linestyle='solid')
        plt.xlabel('log(blog rank)')
        plt.ylabel('log(no. of tweets)')
        plt.show()
    
    def tweetdistribperblog(self):
        blogit = self.db.blogcontent.find()
        tweetdistrib = {}
        numblogs_domain = {}
        for i in blogit:
            domain = i['tweethandle']
            if domain in numblogs_domain:
                numblogs_domain[domain].append(i['id_str'])
            else:
                numblogs_domain[domain] = [i['id_str']]
        print numblogs_domain
        
        for i in numblogs_domain:
            counttweet = 0
            #print i, ": ", len(numblogs_domain[i])
            for tid in numblogs_domain[i]:
                counttweet += self.db.tweets.find({'related_tweet' : tid}).count()
            tweetdistrib[i] = float(counttweet)/(len(numblogs_domain[i]))
        tweetdistrib_sorted = sorted(tweetdistrib.iteritems(), key=operator.itemgetter(1), reverse=True)
        f = open("test1", 'w')
        pickle.dump(tweetdistrib_sorted, f)
        print tweetdistrib
    
    def plottweetdistribperblog(self):
        f = open("test1", 'r')
        distrib = pickle.load(f)
        x = range(len(distrib))
        y = []
        k = []
        for (key,value) in distrib:
            y.append(value)
            k.append(key)
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.bar(x, y, facecolor='#87B570', align='center')
        ax.set_xticks(x)
        ax.set_ylabel('Avg. No. of tweets per blog')
        ax.set_xticklabels(k)
        fig.autofmt_xdate()
        plt.show()
    
    def mostpopularanalysis(self):
        blog = self.db.blogcontent.find({'id_str':self.mostpopular})
        f = open('most_popular_blog', 'w')
        for i in blog:
            pickle.dump(i, f)
        f.close()
        print "numtweets: ", self.mostpopular_nt
        related_tweets = self.db.tweets.find({'related_tweet' : self.mostpopular})
        f = open('most_popular_blog_ts', 'w')
        for i in related_tweets:
            f.write(pickle.dumps(i) + '\n')
        f.close()
    def mostpopulara(self):
        f = open('most_popular_blog_ts', 'r')
        related_tweets = pickle.load(f)
        print related_tweets
        """
        for i in related_tweets:
            print related_tweets[i]
        """
        f.close()
    def dataforannotating(self):
        blogit = self.db.blogcontent.find()
        #tweetdistrib = {}
        numblogs_domain = {}
        for i in blogit:
            domain = i['tweethandle']
            if domain in numblogs_domain:
                numblogs_domain[domain].append(i['id_str'])
            else:
                numblogs_domain[domain] = [i['id_str']]
        print numblogs_domain
        
        loc = config.PROJECT_ROOT + 'data/analyze/'
        #domainwise = {}
        for i in numblogs_domain:
            #counttweet = []
            #print i, ": ", len(numblogs_domain[i])
            for tid in numblogs_domain[i]:
                c = self.db.tweets.find({'related_tweet' : tid})
                """
                if c > 0:
                    counttweet.append({tid: c})
                """
                so = False
                for j in c:
                    #f.write(str(j)+"\n")
                    f = open(loc+i+"_"+tid+".txt", 'w')
                    f.write("{")
                    f.write("text: "+j['text']+",")
                    if ('entities' in j):
                        f.write("entities: "+str(j['entities'])+",")
                    f.write("created_at:"+str(j['created_at'])+",")
                    f.write("from_user_name: "+j["from_user_name"])
                    f.write("}\n")
                    so = True
                if so:
                    f.write("\n---------------------\n")
                    cit = self.db.blogcontent.find({'id_str':tid})
                    for x in cit:
                        f.write(x['url']+"\n")
                        f.write(x['title']+"\n")
                        f.write(x['body']+"\n")
                        f.write(str(x['comments']))
                    f.close()
                else:
                    f.close()
                    os.remove(loc+i+"_"+tid+".txt")
                   
            #domainwise[i] = counttweet

def main(argv=None):
    dp = DataPatterns()
    #dp.findtweetdistrib()
    #dp.plottweetdistrib()
    #dp.tweetdistribperblog()
    #dp.plottweetdistribperblog()
    #dp.mostpopularanalysis()
    dp.dataforannotating()
    

if __name__ == "__main__":
    sys.exit(main())
