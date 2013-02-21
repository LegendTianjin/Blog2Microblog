'''
Created on Mar 31, 2012
@author: vandana
Tweet class forms the building block of tweets facilitated blog summary using recommendation style approach.
'''
from copy import deepcopy

class Tweet:
    
    def __init__(self, tweet):
        #self.rawtweet = tweet
        self.text = tweet['text']
        self.id = tweet['id_str']
        self.relatedblog = tweet['related_tweet']
        self.fromuser = tweet['from_user_id_str']
        self.length = len(self.text)
        self.itemssimscore = []
        self.itemratings = []
        self.predictedratings = [] 
        self.averagetfidfscore = 0
        self.authornumfollowers = 0
        try:
            self.usermentions = tweet['entities']['user_mentions']
            self.hashtags = tweet['entities']['hashtags']
            if len(tweet['entities']['urls']) > 0:
                self.url = tweet['entities']['urls'][0]['expanded_url']	
        except:
            self.usermentions = []
            self.hashtags = []
            self.url = ""
    
    """
    def getrating(self, itemindex):
        ''' given a item, it returns a tweet specific rating for the item based on tweet features '''
        ''' call methods to calculate rating '''
        return 0
    """
    
    def tostring(self):
        string = self.text + ' || ' + self.id + ' || ' 
        return string

"""
class TweetUser:
    def __init__(self, blogid):
        self.blogid = blogid
        self.tweetitem_entry = []
    
    def updatetweetitem(self, tweet, item):
        i = deepcopy(item)
        self.tweetitem_entry.append({'item': i, 'tweet': tweet})
"""