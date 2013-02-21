#Provides Utility functions for text processing
'''
Created on Mar 29, 2012
@author: vandana
'''

import nltk
import math
import re
import os
import pickle
import sys
import config
from pymongo import Connection
from nltk.corpus import stopwords
from blogprocessor import Item
from tweetsprocessor import Tweet
import HTMLParser
import shutil

def getdocvector(text):
    idfpath = config.PROJECT_ROOT+'data/idfs.pickle'
    vector = {}
    tokens = tokenize(text)
    tfs = tf(tokens)
    idfs = idf(tokens, idfpath)
    for i in tfs:
        vector[i] = tfs[i]*idfs[i]
    return vector
    
def tokenize(text):
    pattern = r'''(?x)([A-Z]\.)+| \w+(-\w+)*| \$?\d+(\.\d+)?%?| \.\.\.| [][.,;"'?():-_`]'''
    tokens_r = nltk.regexp_tokenize(text, pattern)
    #tokens_w = nltk.wordpunct_tokenize(text)
    #tokens_basic = re.split(r'\s*[,;.]*\s+', text)
    #print tokens_r
    #print tokens_w
    #print tokens_basic
    return tokens_r
    
def getsents(text):
    #sents_basic = re.split(r'\s*[\.\?!][\)\]]*\s*', text)
    sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sents_r = sent_tokenizer.tokenize(text)
    #print sents_basic
    #print sents_r
    return sents_r
    
def cosinesim(v1, v2):
    num = 0
    for i in v1:
        if i in v2:
            num += v1[i]*v2[i]
    if num == 0:
        return 0
    eulen1 = 0.0
    for i in v1:
        eulen1 += v1[i]**2
    eulen1 = math.sqrt(eulen1)
    eulen2 = 0.0
    for i in v1:
        eulen2 += v1[i]**2
    eulen2 = math.sqrt(eulen2)
    denom = eulen1 * eulen2
    return num/denom
    
def tf(text):
    tfs = {}
    punctpattern = re.compile(r'[,;\'"\)\(}{\[\].!\?<>=+-/*\\:]+')
    numpattern = re.compile(r'[0-9]+')
    if isinstance(text, basestring):
        tokens = tokenize(text)
    else:
        #already tokenized
        tokens = text
    for i in tokens:
        if i in stopwords.words('english') or punctpattern.match(i) != None or numpattern.match(i) != None:
            continue
        if i in tfs:
            tfs[i] += 1
        else:
            tfs[i] = 1
    return tfs
    
def idf(text, idffilepath, n=40000):
    idfs = {}
    punctpattern = re.compile(r'[,;\'\"\)\(}{\[\].!\?<>=+-/*\\:]+')
    numpattern = re.compile(r'[0-9]+')
    f = open(idffilepath, 'r')
    idfmap = pickle.load(f)
    if isinstance(text, basestring):
        tokens = tokenize(text)
    else:
        tokens = text
    for i in tokens:
        if i in stopwords.words('english') or punctpattern.match(i) != None or numpattern.match(i) != None:
            continue
        if i not in idfs:
            if i in idfmap:
                idfs[i] = idfmap[i]
            else:
                #n: size of document corpus
                idfs[i] = math.log(n)
    return idfs

def getsimscore(doc1, doc2):
    v1 = getdocvector(doc1)
    v2 = getdocvector(doc2)
    s = cosinesim(v1, v2)
    return s

def getavgtfidf(text):
    tfs = tf(text)
    idfs = idf(text, config.PROJECT_ROOT+'data/idfs.pickle')
    s = 0.0
    c = 0
    for i in tfs:
        s += tfs[i]*idfs[i]
        c += 1
    if c == 0:
        return 0
    return (s/c)

def getitems(title, parascontent):
    paras_p = []
    for i in parascontent:
        para = re.sub('(\.)(\w+)', '\g<1> \g<2>', i)
        para = re.sub(r"(\w+)\\'", "\g<1>'", para)
        #para = re.sub(r'(\$.*)|(.*\);)|(.*=.*\s*)|(\s*.*\w+.*:.*\s*)|(google_ad_.*;*\s*)|(/\*.*\*/)|(.*div.*>.*</div.*)|(.*{+.*}+.*)|(.*{.*)|(.*[Aa][dD]s*.*)|(.*}.*\s+)', '', para)
        para = re.sub(r'(\s)\s+', '\g<1>', para)
        para = para.strip('\t\n \r\f\v')
        if para != '':
            paras_p.append(para)
            
    items = []
    l = len(paras_p)
    docpos = 0
    for p in range(l):
        sents = getsents(paras_p[p])
        for k in range(len(sents)):
            psent = sents[k]
            titlesimscore = getsimscore(psent, title)
            avgtfidf = getavgtfidf(psent)
            item = Item(psent, docpos+1, p+1, k+1, title, titlesimscore, avgtfidf)
            items.append(item)
            docpos += 1
    return items

def gettweets(tweetsjsonarr, items, title):
    tweets = []
    ignorepattern = re.compile(r'^' + title + r'.*\s+http://.*\s*')
    for i in tweetsjsonarr:
        twt = Tweet(i)
        if ignorepattern.search(twt.text) != None:
            continue
        itemsimscore = []
        for j in items:
            itemsimscore.append(getsimscore(twt.text, j.content))
            twt.itemratings.append(j.userinterestrating)
        twt.itemssimscore = itemsimscore
        twt.averagetfidfscore = getavgtfidf(twt.text)
        tweets.append(twt)
    return tweets

def informationgaincompare(doc, text1, text2):
    text1a = tokenize(text1)
    text2a = tokenize(text2)
    t1 = []
    t2 = []
    punctpattern = re.compile(r'[,;\'"\)\(}{\[\].!\?<>=+-/*\\:]+')
    for i in text1a:
        if i in stopwords.words('english') or punctpattern.match(i) != None:
            continue
        t1.append(i)
    for i in text2a:
        if i in stopwords.words('english') or punctpattern.match(i) != None:
            continue
        t2.append(i)
    doctokens = tokenize(doc)
    docwords = []
    for i in doctokens:
        if i in stopwords.words('english') or punctpattern.match(i) != None:
            continue
        docwords.append(i)
    count1 = 0
    for i in t1:
        count1 += docwords.count(i)
    count2 = 0
    for i in t2:
        count2 +=docwords.count(i)
    l = len(docwords)
    p1 = float(count1)/l
    p2 = float(count2)/l
    return (-p1*math.log(p1), -p2*math.log(p2))
        
class BlogCorpus:
    
    def __init__(self):
        dbConn = Connection("localhost", 27017)
        self.db = dbConn.b2mb
        self.htmlparser = HTMLParser.HTMLParser()
         
    def generatedocumentfiles(self, path):
        #blogs_it = self.db.blogcontent.find({"tweethandle":"techcrunch", "id_str":"184854937279279104", "body":{"$ne" : ""}, "paras":{"$ne" : ""}, "paras":{"$ne" : []}})
        blogs_it = self.db.blogcontent.find({"body":{"$ne" : ""}, "paras":{"$ne" : ""}, "paras":{"$ne" : []}})
        k = 0
        for blog in blogs_it:
            d = path + blog['tweethandle']
            if not os.path.exists(d):
                os.mkdir(d)
                os.mkdir(d+'/sentences')
                os.mkdir(d+'/content')
                os.mkdir(d+'/items')
            #self.gendocparasfile(blog, d)
            #self.gendocfile(blog, d)
            self.genitemsfile(blog, d)
            k += 1
            print k, " ", blog['id_str']
    
    def gendocfile(self, doc, path):
        fn = doc['id_str'] + '.txt'
        f = open(path+'/sentences/'+fn, 'w')
        doc['body'] = re.sub('(\.)(\w+)', '\g<1> \g<2>', doc['body'])
        sents = getsents(doc['body'])
        for i in sents:
            #i = re.sub(r'(\$.*\s)|(.*\);\s+)|(\s+.*\w+.*:.*\s?)|(.*=.*\s?)|(google_ad_.*;*\s*)|(/\*.*\*/)|(.*div.*>.*</div.*)|(.*{+.*}+.*)|(.*{.*)|(.*((Ads\s)|(ADVERTISEMENT\s?)|(ADS\s)).*\s)|(.*}.*\s)', '', i)
            i = re.sub(r'(google_ad_.*;*\s*)|(/\*.*\*/)|(.*div.*>.*</div.*)|(.*{+.*}+.*)|(.*{.*)|(.*((Ads\s)|(ADVERTISEMENT\s?)|(ADS\s)).*\s)|(.*}.*\s)', '', i)
            i = re.sub(r'(\s)\s+', '\g<1>', i)
            i = i.strip('\t\n \r\f\v')
            if i != '':
                print i, "@@@",
                f.write(i+'\n')
        print doc['url']
        f.close()
    
    def genitemsfile(self, doc, path):
        #fb = open(path+'/sentences/'+doc['id_str']+'.txt', 'r')
        #c = 0
        paras = self.gendocparasfile(doc, path, True)
        items = []
        l = len(paras)
        """
        for i in fb:
            found = False
            sent = unicode(i).strip('\t\n \r\f\v')
            for p in range(l):
                sents = getsents(paras[p])
                for k in range(len(sents)):
                    psent = sents[k]
                    if sent in psent:
                        #titlesimscore = getsimscore(sent, doc['title'])
                        #avgtfidf = getavgtfidf(sent)
                        titlesimscore = avgtfidf = 0
                        item = Item(sent, c, p, k, doc['title'], titlesimscore, avgtfidf)
                        items.append(item)
                        c += 1
                        found = True
                        break
                if found:
                    break
        """
        docpos = 0
        for p in range(l):
            sents = getsents(paras[p])
            for k in range(len(sents)):
                psent = sents[k]
                titlesimscore = avgtfidf = 0
                item = Item(psent, docpos+1, p+1, k+1, doc['title'], titlesimscore, avgtfidf)
                items.append(item)
                docpos += 1
                   
        l1 = len(items)
        if l1 > 0:
            f = open(path+'/items/'+doc['id_str']+'.txt', 'w')
            for i in items:
                print i.tostring()
                f.write(i.tostringfile()+'\n')
            f.close()
            f1 = open(path+'/items/'+doc['id_str']+'.pickle', 'w')
            pickle.dump(items, f1)
            f1.close()
    
    def updateitems(self, path):
        for (root, dir, files) in os.walk(path):
            for f in files:
                if 'items' in root and '.pickle' in f:
                    pf = open(root+'/'+f, 'r')
                    items = pickle.load(pf)
                    pf.close()
                    idstr = f.split('.')[0]
                    title_it = self.db.blogcontent.find({"id_str":idstr})
                    title = ""
                    for t in title_it:
                        title = t['title']
                    for i in items:
                        i.titlesimilarityscore = getsimscore(i.content, title)
                        i.averagetfidfscore = getavgtfidf(i.content)
                        print i.tostring()
                    print idstr
                    pf = open(root+'/'+f, 'w')
                    pickle.dump(items, pf)
                    pf.close()
    
    def gendocparasfile(self, doc, path, arr=False):
        fn = doc['id_str'] + '_c.txt'
        paras = doc['paras']
        if not arr:
            f = open(path+'/content/'+fn, 'w')
            f.write(doc['title']+'\n')
            print doc['title']
            #print paras
            for i in paras:
                para = re.sub('(\.)(\w+)', '\g<1> \g<2>', i)
                #para = re.sub(r'(\$.*)|(.*\);)|(.*=.*\s*)|(\s*.*\w+.*:.*\s*)|(google_ad_.*;*\s*)|(/\*.*\*/)|(.*div.*>.*</div.*)|(.*{+.*}+.*)|(.*{.*)|(.*[Aa][dD]s*.*)|(.*}.*\s+)', '', para)
                para = re.sub(r'(\s)\s+', '\g<1>', para)
                para = para.strip('\t\n \r\f\v')
                if para != '':
                    print para, "@@@",
                    f.write(i+'\n\n')
            print doc['url']
            f.close()
            return ""
        else:
            paras_p = []
            for i in paras:
                para = re.sub('(\.)(\w+)', '\g<1> \g<2>', i)
                para = re.sub(r"(\w+)\\'", "\g<1>'", para)
                #para = re.sub(r'(\$.*)|(.*\);)|(.*=.*\s*)|(\s*.*\w+.*:.*\s*)|(google_ad_.*;*\s*)|(/\*.*\*/)|(.*div.*>.*</div.*)|(.*{+.*}+.*)|(.*{.*)|(.*[Aa][dD]s*.*)|(.*}.*\s+)', '', para)
                para = re.sub(r'(\s)\s+', '\g<1>', para)
                para = para.strip('\t\n \r\f\v')
                if para != '':
                    paras_p.append(para)
            return paras_p
    
    def idf(self, idffilepath, path):
        
        """ Using the paragraphs text files as they have the title also included """
        wordmap = {}
        n = 0
        punctpattern = re.compile(r'[,;\'"\)\(}{\[\].!\?<>=+-/*\\:]+')
        numpattern = re.compile(r'[0-9]+')
        
        for (root, dirs, files) in os.walk(path):
            if "content" in root:
                for f in files:
                    f1 = open(os.path.join(root+'/'+f), 'r')
                    lines = f1.readlines()
                    for l in lines:
                        """ Every line is a para which needs to be broken into sentences to get a count of words per document as our documents here are individual sentences. """
                        l = l.strip('\n')
                        if l != '':
                            sents = getsents(l)
                            n += len(sents)
                            for k in sents:
                                alreadyupdated = {}
                                words = tokenize(k)
                                valid_words = []
                                for w in words:
                                    if w in stopwords.words('english') or punctpattern.match(w) != None or numpattern.match(w) != None:
                                        continue
                                    else:
                                        valid_words.append(w)
                                        alreadyupdated[w] = False
                                for w in valid_words:
                                    if w in wordmap:
                                        if alreadyupdated[w]:
                                            continue
                                        wordmap[w] += 1
                                    else:
                                        wordmap[w] = 1
                                    alreadyupdated[w] = True
                    f1.close()
        print n
        f = open(idffilepath+'idfs.txt', 'w')
        for j in wordmap:
            wordmap[j] = math.log(n/wordmap[j])
            f.write(j+' '+str(wordmap[j])+'\n')
        f.close()
        f1 = open(idffilepath+'idfs.pickle', 'w')
        pickle.dump(wordmap, f1)
        f1.close()
    
    def gettweets(self, path):
        """ creates the tweets folder for each collected and useful blog """
        #tweet_folder = 'tweets'
        tweet_folder = 'tweets_analyze'
        tweet_folder1 = 'tweets'
        for (root, dirs, files) in os.walk(path):
            if "content" in root and "nytimes" not in root:
                for f in files:
                    idstr = f.split('_')[0]
                    if not os.path.exists(root+'/../'+tweet_folder):
                        os.mkdir(root+'/../'+tweet_folder)
                        os.mkdir(root+'/../'+tweet_folder1)
                    f1 = open(root+'/'+f, 'r')
                    lines = f1.readlines()
                    p = root+'/../'+tweet_folder+'/'
                    p_objs = root+'/../'+tweet_folder1+'/'
                    self.genrelatedtweets(idstr, p, p_objs, lines)
                    f1.close()
    
    def genrelatedtweets(self, idstr, path, pathobjs, content=None, arr=False):
        tweets_it = self.db.tweets.find({'related_tweet': idstr})
        """ generate tweet & user objects """
        tweets = []
        for i in tweets_it:
            tweets.append(Tweet(i))
        if len(tweets) == 0:
            return
        if not arr:
            f = open(path+idstr+'.txt', 'w')
            if content:
                f.writelines(content)
                f.write('\n')
            for i in tweets:
                print i.tostring()
                try:
                    f.write(i.tostring()+'\n')
                except:
                    f.write(i.tostring().encode('ascii', 'ignore')+'\n')
            f.close()
            t = open(pathobjs+idstr+'.pickle', 'w')
            pickle.dump(tweets, t)
            t.close()
        else:
            return tweets
    
    def updatetweets(self, path):
        pattern = re.compile(r'[0-9]*\.txt$')
        usefulitems = []
        for (root, dir, files) in os.walk(path):
            if 'itemratings' in root and 'mashable' in root:
                for f in files:
                    if pattern.match(f) != None:
                        idstr = f.split(".")[0]
                        usefulitems.append(idstr)
                break
        print len(usefulitems)
        for (root, dir, files) in os.walk(path):
            if 'treehugger' in root:
                sep = r'\s+:\s+'
            elif 'engadget' in root:
                sep = '\s+--\s+'
            elif 'fakingnews' in root:
                sep = '\s+|\s+'
            else:
                sep = ""
            if 'tweets' in root and 'analyze' not in root and 'mashable' in root:
                for f in files:
                    fname = f.split(".")[0]
                    if '.pickle' in f and fname in usefulitems:
                        pf = open(root+'/'+f, 'r')
                        tweets = pickle.load(pf)
                        pf.close()
                        print f
                        #idstr = f.split('.')[0]
                        fitems = open(root+'/../items/'+f, 'r')
                        items = pickle.load(fitems)
                        fitems.close()
                        tweets1 = []
                        title = items[0].title
                        if sep != "":
                            title = re.split(sep, title)[0]
                        ignorepattern = re.compile(self.htmlparser.unescape(title) + r'.*\s+http://.*\s*')
                        for i in tweets:
                            if ignorepattern.search(i.text) != None:
                                continue
                            itemsimscore = []
                            for j in items:
                                itemsimscore.append(getsimscore(i.text, j.content))
                                i.itemratings.append(j.userinterestrating)
                            i.itemssimscore = itemsimscore
                            i.averagetfidfscore = getavgtfidf(i.text)
                            #print i.tostring()
                            tweets1.append(i)
                        #pf = open(root+'/'+f, 'w')
                        pf1 = open(root+'/../itemtweets/'+f, 'w')
                        #pickle.dump(tweets1, pf)
                        pickle.dump(tweets1, pf1)
                        #pf.close()
                        pf1.close()
    
    def updateitemtargetratings(self, path):
        pattern = re.compile(r'[0-9]*\.txt$')
        for (root, dir, files) in os.walk(path):
            if 'itemratings' in root and ('mashable' in root or 'fakingnews' in root):
                for f in files:
                    if pattern.match(f) == None:
                        continue
                    fp = open(root+'/'+f, 'r')
                    itemrs = []
                    userrs = []
                    idstr = f.split('.')[0]
                    print idstr
                    for line in fp:
                        print line
                        m = re.search(r'(\d+\s\|\|\s\d+)\s*\n', line, re.IGNORECASE)
                        rs = m.group(1).split(' || ')
                        itemrs.append(int(rs[0]))
                        userrs.append(int(rs[1]))
                    fp.close()
                    fitems = open(root+'/../items/'+idstr+'.pickle', 'r')
                    items = pickle.load(fitems)
                    fitems.close()
                    for i in range(len(items)):
                        items[i].targetrating = itemrs[i]
                        items[i].userinterestrating = userrs[i]
                    fitems = open(root+'/../items/'+idstr+'.pickle', 'w')
                    pickle.dump(items, fitems)
                    fitems.close()
            
def copyitems(path):
    ids = {}
    for (root, dir, files) in os.walk(path):
        if "tweets_analyze/use" in root:
            blogname = root.split('/')[7]
            ids[blogname] = []
            for f in files:
                ids[blogname].append(f)
    for (root, dir, files) in os.walk(path):
        if "items" in root:
            blogname = root.split('/')[7]
            for f in files:
                if f in ids[blogname]:
                    shutil.copy2(root+'/'+f, root+'/../itemratings/')

def main(argv=None):
    path = config.PROJECT_ROOT + 'data/blogs/'
    bc = BlogCorpus()
    #bc.generatedocumentfiles(path)
    #bc.updateitems(path)
    
    ''' Calculate IDFs for the entire corpus '''
    #bc.idf(config.PROJECT_ROOT+'data/', path)
    
    ''' related tweets '''
    #bc.gettweets(path)
    bc.updatetweets(path)
    
    ''' some copying around '''
    #copyitems(path)
    
    #bc.updateitemtargetratings(path)
    
    

if __name__ == '__main__':
    sys.exit(main())
        
