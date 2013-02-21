'''
Created on Apr 21, 2012
@author: vandana
This module is for model and summarization tool evaluation
'''

import os
import sys
import pickle
import json
import re
import ratingslearner
import recommendersystem
import config
import util
import crawler

class Evaluation:
    def __init__(self):
        self.precision = 0
        self.recall = 0
        self.coverage = 0
        self.titleMI = 0
    
    def evaluatethesummary(self, path, recommender=False):
        blogsitems = {}
        summaries = []
        blogs = []
        for (root, dir, files) in os.walk(path):
            if 'items' in root:
                for i in files:
                    fi = open(root+'/'+i, 'r')
                    name = i.split('.')[0]
                    blogsitems[name] = pickle.load(fi)
        if recommender:
            blogstweets = {}
            for (root, dir, files) in os.walk(path):
                if 'tweets' in root:
                    for i in files:
                        ft = open(root+'/'+i, 'r')
                        name = i.split('.')[0]
                        blogstweets[name] = pickle.load(ft)
            for i in blogsitems:
                r = recommendersystem.Recommender(0.5)
                r.creatematrix(blogsitems[i], blogstweets[i])
                r.calcaggregateratings()
                items = r.getrecommenderrateditems()
                if items == []:
                    print "error evaluating... recommender itemratings could not be calculated"
                    return
                else:
                    sorted_items = sorted(items, key=lambda k: k['rating'], reverse=True)
                    sorted_items = sorted_items[:5]
                    sorted_items = sorted(sorted_items, key=lambda k: k['position'])
                    summaries.append(sorted_items)
                    blogs.append(items)
        else:
            for i in blogsitems:
                response = ratingslearner.predictratings(blogsitems[i])
                response = json.loads(response)
                if response == None or response['status'] == 400:
                    print "error evaluating... itemratings could not be calculated"
                    return
                items = response['content']
                for i in items:
                    print i['text'], i['rating'], i['position']
                sorted_items = sorted(items, key=lambda k: k['rating'], reverse=True)
                sorted_items = sorted_items[:5]
                sorted_items = sorted(sorted_items, key=lambda k: k['position'])
                summaries.append(sorted_items)
                blogs.append(items)
        
        g = GroundTruth(blogs)
        for i in range(len(summaries)):
            g.comparewithgroundtruth(summaries[i], i)
    
    def skimthatevaluation(self, path):
        arr = {}
        f = open(path+'original_urls', 'r')
        for line in f:
            line = line.split(" ")
            arr[line[0]] = line[1]
        
        g = SkimThatGroundTruth(arr, path)
        
        for i in arr:
            domain = ""
            if re.search(r'news\.cnet', arr[i]) != None:
                domain = 'cnetnews'
            if domain == "":
                print "error in domain"
                return
            bh = crawler.BlogHtml(arr[i], domain)
            items = util.getitems(bh.title, bh.blogparas)
            response = ratingslearner.predictratings(items)
            response = json.loads(response)
            if response == None or response['status'] == 400:
                print "error evaluating... itemratings could not be calculated"
                return
            items = response['content']
            """
            for i in items:
                print i['text'], i['rating'], i['position']
            """
            sorted_items = sorted(items, key=lambda k: k['rating'], reverse=True)
            sorted_items = sorted_items[:5]
            sorted_items = sorted(sorted_items, key=lambda k: k['position'])
            sim = g.comparewithskimthatgroundtruth(sorted_items, i)
            print 'cosine similarity: ', sim

class GroundTruth:
    def __init__(self, blogsarr):
        self.blogsarr = blogsarr
        self.humansummary = self.computehumansummary()
    
    def computehumansummary(self):
        summaries = []
        ''' blogsarr is an array of blogs where each entry is a list of items. '''
        for items in self.blogsarr:
            sorted_items = sorted(items, key=lambda k: k['targetrating'], reverse=True)
            sorted_items = sorted_items[:5]
            sorted_items = sorted(sorted_items, key=lambda k: k['position'])
            summaries.append(sorted_items)
        return summaries
    
    def comparewithgroundtruth(self, summary, index):
        intersection = []
        for i in summary:
            if self.containshumansummary(i['text'], index):
                intersection.append(i)
        l = len(intersection)
        precision = float(l)/len(summary)
        recall = float(l)/len(self.humansummary[index])
        f1 = 2*precision*recall/(precision + recall)
        print precision, recall, f1
        return {'precision': precision, 'recall':recall, 'f1':f1}
    
    def containshumansummary(self, text, index):
        for i in self.humansummary[index]:
            if i['text'] == text:
                return True
        return False

''' class for comparison with other tools '''    
class SkimThatGroundTruth:
    def __init__(self, blogsarr, path):
        self.blogsarr = blogsarr
        self.skimthatsummary = self.getskimthatsummary(blogsarr, path)
        #self.greatsummary = [] #server down
    
    def comparewithskimthatgroundtruth(self, summary, index):
        skimthatsumm = self.skimthatsummary[index]
        skimthat = " ".join(skimthatsumm)
        summs = [i['text'] for i in summary]
        s = " ".join(summs)
        print skimthatsumm
        print '----'
        print s
        sim = util.getsimscore(s, skimthat)
        return {'similarity': sim}
    
    def getskimthatsummary(self, blogsarr, path):
        skimthatsummaries = {}
        for i in blogsarr:
            f = open(path+i+'.txt', 'r')
            skimthatsummaries[i] = f.readlines()
        return skimthatsummaries
        
        
def main(argv=None):
    e = Evaluation()
    #e.evaluatethesummary(config.PROJECT_ROOT+'data/groundtruth/', True)
    e.skimthatevaluation(config.PROJECT_ROOT+'data/skimthat/cnetnews/')
    
if __name__ == '__main__':
    sys.exit(main())