'''
Created on Apr 20, 2012
@author: vandana
The Recommender System creates a utility matrix, for document and tweet ratings for the summarization task.
'''
import json
import ratingslearner

class Recommender:
    def __init__(self, lambda1):
        self.utilitymatrix = {}
        self.lambda1 = lambda1
        self.items = []
        self.tweets = []
    
    def creatematrix(self, items, tweets):
        response = ratingslearner.predictratings(items)
        response = json.loads(response)
        if response == None or response['status'] == 400:
            return
        items1 = response['content']
        """
        for i in items1:
            print i['text'], i['rating'], i['position']
        """
        self.items = items1
        response1 = ratingslearner.predicttweetratings(tweets)
        response1 = json.loads(response1)
        if response1 == None or response1['status'] == 400:
            return
        tweets1 = response1['content']
        """
        for i in tweets1:
            print i['text'], i['predictedratings'], i['id']
        """
        self.tweets = tweets1
        ratingrow = []
        for i in items1:
            ratingrow.append(i['rating'])
        self.utilitymatrix['docrow'] = ratingrow
        id_indexer = {}
        for i in tweets1:
            self.utilitymatrix[i['id']] = i['predictedratings']
            id_indexer[i['id']] = i

        self.supporttweets = []
        self.supportratings = []
        l = len(items1)
        for i in range(l):
            self.supporttweets.append("")
            self.supportratings.append(-1234)
        for i in self.utilitymatrix:
            if i != 'docrow':
                for j in range(l):
                    if self.utilitymatrix[i][j] > self.supportratings[j]:
                        self.supportratings[j] = self.utilitymatrix[i][j]
                        self.supporttweets[j] = id_indexer[i]
    
    def calcaggregateratings(self):
        #for average tweet ratings we can take weighted average in terms of author's characteristics (author's popularity or page rank)
        #for now taking simple average
        docratings = self.utilitymatrix['docrow']
        l = len(docratings)
        tweetaggregate = []
        for i in range(l):
            tweetaggregate.append(0)
        count = 0
        for i in self.utilitymatrix:
            if i != 'docrow':
                for j in range(l):
                    tweetaggregate[j] += self.utilitymatrix[i][j]
                count += 1
        for i in range(l):
            tweetaggregate[i] = tweetaggregate[i]/count
        self.tweetaggregate = tweetaggregate
        aggregate = []
        for i in range(l):
            aggregate.append(self.lambda1*docratings[i] + (1-self.lambda1)*tweetaggregate[i])
        self.aggregateratings = aggregate
        
    def getrecommenderrateditems(self):
        if not hasattr(self, 'aggregateratings'):
            return []
        else:
            l = len(self.items)
            for i in range(l):
                self.items[i]['rating'] = self.aggregateratings[i]
                self.items[i]['tweetrating'] = self.tweetaggregate[i]
                if self.supporttweets[i] != "":
                    self.items[i]['supporttweet'] = self.supporttweets[i]['text']
                if self.supportratings[i] != -1234:
                    self.items[i]['supporttweetrating'] = self.supportratings[i]
        return self.items