'''
Created on Apr 3, 2012
@author: vandana
RatingsLearner processes the items and user objects to learn ratings model based on sentence and tweet features in a blog.
Once the model is ready it can be used to generate ratings for new blogs. 
'''
import config
import os
import pickle
import random
import sys
import json
from sklearn import svm, linear_model, tree
#from sklearn.naive_bayes import GaussianNB

class RatingsLearner:
    def __init__(self, traindata=None):
        self.traindata = traindata
        if traindata:
            (self.X, self.Y) = self.processdata(self.traindata)
        self.model = None
    
    def processdata(self, tdata):
        tdataX = []
        tdataY = []
        for item in tdata:
            x = []
            x.append(item.docposition)
            x.append(item.inpara)
            x.append(item.paraposition)
            x.append(item.averagetfidfscore)
            x.append(item.titlesimilarityscore)
            x.append(item.length)
            tdataX.append(x)
            tdataY.append(item.targetrating)
        return (tdataX, tdataY)
    
    def learn(self):
        svr_lin = svm.SVR(kernel='linear', C=1, degree=2)
        svr_lin.fit(self.X, self.Y)
        y_lin = svr_lin.predict(self.X)
        self.model = svr_lin
        #f = open(config.PROJECT_ROOT+'data/ratingsmodel.pickle', 'w')
        f = open(config.PROJECT_ROOT+'data/ratingsmodel1.pickle', 'w')
        pickle.dump(svr_lin, f)
        f.close()
        """
        clf = linear_model.LinearRegression()
        clf.fit(self.X, self.Y)
        
        clf = tree.DecisionTreeRegressor(max_depth=5)
        clf.fit(self.X, self.Y)
        """
        """
        clf = GaussianNB()
        clf.fit(self.X, self.Y)
        
        y_lin = clf.predict(self.X)
        self.model = clf
        """
        print y_lin
        print self.Y
    
    def predict(self, data, loadfromfile=False, accuracy=False):
        response = {}
        if not data:
            response['status'] = 400
            response['content'] = []
        else:
            (tdataX, tdataY) = self.processdata(data)
            if loadfromfile:
                #f = open(config.PROJECT_ROOT+'data/ratingsmodel.pickle', 'r')
                f = open(config.PROJECT_ROOT+'data/ratingsmodel1.pickle', 'r')
                model = pickle.load(f)
                f.close()
                y = model.predict(tdataX)
            else:
                y = self.model.predict(tdataX)
            
            ''' for debugging '''
            if accuracy:
                print '-------------------------------'
                print y
                print tdataY
                avgerr = 0
                for i in range(len(y)):
                    avgerr += y[i] - tdataY[i]
                    print y[i] - tdataY[i]
                avgerr = (avgerr/len(y))
                print avgerr
            
            response['status'] = 200
            for i in range(len(data)):
                data[i].rating = y[i]
            content = []
            for i in data:
                obj = {}
                obj['text'] = i.content
                obj['rating'] = i.rating
                obj['position'] = i.docposition
                obj['targetrating'] = i.targetrating
                content.append(obj)
            response['content'] = content
        return json.dumps(response)

class TweetsRatingsLearner:
    def __init__(self, traindata=None, testdata=None):
        self.traindata = traindata
        self.testdata = testdata
        if traindata:
            (self.X, self.Y) = self.processdata(self.traindata)
        self.model = None
    
    def processdata(self, tdata):
        tdataX = []
        tdataY = []
        for tweet in tdata:
            l = len(tweet.itemssimscore)
            for j in range(l):
                x = []
                x.append(tweet.itemssimscore[j])
                x.append(tweet.averagetfidfscore)
                x.append(tweet.length)
                #x.append(tweet.authornumfollowers)
                tdataX.append(x)
                tdataY.append(tweet.itemratings[j])
        return (tdataX, tdataY)
    
    def learn(self):
        svr_lin = svm.SVR(kernel='linear', C=1, degree=2)
        svr_lin.fit(self.X, self.Y)
        y_lin = svr_lin.predict(self.X)
        self.model = svr_lin
        #f = open(config.PROJECT_ROOT+'data/tweetratingsmodel.pickle', 'w')
        f = open(config.PROJECT_ROOT+'data/tweetratingsmodel1.pickle', 'w')
        pickle.dump(svr_lin, f)
        f.close()
        """
        clf = linear_model.LinearRegression()
        clf.fit(self.X, self.Y)
        
        clf = tree.DecisionTreeRegressor(max_depth=5)
        clf.fit(self.X, self.Y)
        """
        """
        clf = GaussianNB()
        clf.fit(self.X, self.Y)
        
        y_lin = clf.predict(self.X)
        self.model = clf
        """
        print y_lin
        print self.Y
    
    def predict(self, data, loadfromfile=False, accuracy=False):
        response = {}
        if not data or len(data) == 0:
            response['status'] = 400
            response['content'] = []
        else:
            (tdataX, tdataY) = self.processdata(data)
            if loadfromfile:
                #f = open(config.PROJECT_ROOT+'data/tweetratingsmodel.pickle', 'r')
                f = open(config.PROJECT_ROOT+'data/tweetratingsmodel1.pickle', 'r')
                model = pickle.load(f)
                f.close()
                y = model.predict(tdataX)
            else:
                y = self.model.predict(tdataX)
            
            ''' for debugging '''
            if accuracy:
                print '-------------------------------'
                print y
                print tdataY
                avgerr = 0
                for i in range(len(y)):
                    avgerr += y[i] - tdataY[i]
                    print y[i] - tdataY[i]
                avgerr = (avgerr/len(y))
                print avgerr
            
            response['status'] = 200
            start = 0
            for i in range(len(data)):
                l = len(data[i].itemratings)
                #print y[start:start+l]
                data[i].predictedratings = y[start:start+l].tolist()
                start = l
            content = []
            for i in data:
                obj = {}
                obj['text'] = i.text
                obj['id'] = i.id
                obj['itemratings'] = i.itemratings
                obj['predictedratings'] = i.predictedratings 
                content.append(obj)
            response['content'] = content
        return json.dumps(response)
    
def main(argv=None):
    tdata = []
    fnames = []
    path = config.PROJECT_ROOT + 'data/blogs/'
    for (r, d, fs) in os.walk(path):
        if 'itemratings' in r and ('mashable' in r or 'fakingnews' in r or 'treehugger' in r):
            for f in fs:
                name = f.split('.')[0]+'.pickle'
                fnames.append(name)
    
    for (root, dir, files) in os.walk(path):
        if 'items' in root and ('mashable' in root or 'fakingnews' in root or 'treehugger' in root):
            for f in files:
                if '.pickle' in f and f in fnames:
                    fp = open(root+'/'+f, 'r')
                    items = pickle.load(fp)
                    fp.close()
                    tdata.extend(items)
    random.shuffle(tdata)
    size = len(tdata)
    size_train = int((80*size)/100)
    traindata = tdata[:size_train]
    testdata = tdata[size_train:]
    rl = RatingsLearner(traindata)
    rl.learn()
    rl.predict(testdata, accuracy=True)
    
    '''--------tweets---------'''
    for (root, dir, files) in os.walk(path):
        if 'itemtweets' in root and ('mashable' in root or 'fakingnews' in root or 'treehugger' in root):
            for f in files:
                if '.pickle' in f:
                    fp = open(root+'/'+f, 'r')
                    tweets = pickle.load(fp)
                    fp.close()
                    tdata.extend(tweets)
    random.shuffle(tdata)
    size = len(tdata)
    size_train = int((80*size)/100)
    traindata = tdata[:size_train]
    testdata = tdata[size_train:]
    rl = TweetsRatingsLearner(traindata)
    rl.learn()
    rl.predict(testdata, accuracy=True)

def predictratings(tdata):
    rl = RatingsLearner()
    return rl.predict(tdata, True)

def predicttweetratings(tdata):
    rl = TweetsRatingsLearner()
    return rl.predict(tdata, True)

if __name__ == '__main__':
    sys.exit(main())