'''
Created on Mar 22, 2012
@author: vandana
Contains the Item class. Each sentence of a blog is represented by an Item object.
'''
"""
import re
import sys
import os
import config
import tarfile
from pymongo import Connection
from crawler import BlogHtml
"""

class Item:
    #rel positions are ranks of appearance of sentences in document and paras
    def __init__(self, sent, docrelpos, para, pararelpos, title, titlesimscore, avgtfidf, targetrating=0):
        self.content = sent
        self.docposition = docrelpos
        self.inpara = para
        self.paraposition = pararelpos
        # call functions here
        self.tfidf_terms = []
        self.averagetfidfscore = avgtfidf
        #this value populated only for train and test data
        self.targetrating = targetrating
        self.userinterestrating = 0
        #the model calculated rating
        self.rating = 0
        self.title = title
        self.titlesimilarityscore = titlesimscore
        self.length = len(sent)
    
    def updatetargetratings(self, r, u):
        self.targetrating = r
        self.userinterestrating = u
    
    def tostring(self):
        dic = {'text': self.content, 'docposition': self.docposition, 'inpara': self.inpara, 'parapos': self.paraposition, 'len': self.length, 'titlesimscore':self.titlesimilarityscore, 'avgtfidf': self.averagetfidfscore}
        return str(dic)
    
    def tostringfile(self):
        string = self.content + ' || ' + str(self.docposition) + ' || ' + str(self.inpara) + ' || ' + str(self.paraposition) + ' || ' + str(self.length) + ' || '
        return string

"""
class BlogProcessor:
    end_punctuation = ['.', '?', '!']
    def __init__(self):
        self.items = []
        dbConn = Connection("localhost", 27017)
        self.db = dbConn.b2mb
        self.blogcontentpath = config.PROJECT_ROOT + 'data/blogcontent/'
    
    def getsents(self, blogcontent):
        sents = re.split(r'\s*[\.\?!][\)\]]*\s*', blogcontent)
        return sents
    
    def getparas(self, id_str, domain):
        tarpath = self.blogcontentpath + domain + ".tar.gz" 
        tar = tarfile.open(tarpath, "r:gz")
        tar.extract(id_str+".html", self.blogcontentpath)
        htmlfile = open(self.blogcontentpath+id_str+".html", 'r')
        if htmlfile:
            html = "".join(htmlfile.readlines())
            bh = BlogHtml()
            paras = bh.getcontentparas(html, domain)
            return paras
        else:
            return ""

    def getcontent(self, id_str, domain):
        try:
            it = self.db.blogcontent.find({'id_str': id_str})
            sents = []
            title = ""
            paras = []
            for i in it:
                title = i['title']
                sents = self.getsents(i['body'])
                #paras = self.getparas(id_str, domain)
                paras = i['paras']
            ls = len(sents)
            l = len(paras)
            for x in range(ls):
                sents[x] = re.sub(r'google.*=.*;', '', sents[x])
                sents[x] = sents[x].strip()
                sents[x] = re.sub(r'(\s)\s+', '\g<1>', sents[x])
                sents[x] = re.sub(r'\s+([;,])', r'\g<1>', sents[x])
            for x in range(l):
                paras[x] = paras[x].strip()
                paras[x] = re.sub(r'(\s)\s+', '\g<1>', paras[x])
                paras[x] = re.sub(r'\s+\,', r',', paras[x])
            sents = filter(None, sents)
            paras = filter(None, paras)
            print title
            print sents
            print paras
            the_item_sents = []
            sentrank = 0
            prevparaindexes = []
            l = len(paras)
            for i in range(len(sents)):
                for j in range(l):
                    if sents[i] and sents[i].strip() in paras[j]:
                        l1 = len(prevparaindexes)
                        if j+1 <= l1:
                            prevparaindexes[j].append(1)
                        else:
                            prevparaindexes.append([1])
                        pararank = len(prevparaindexes[j]) - 1
                        item = Item(sents[i], sentrank, j, pararank, title)
                        sentrank += 1
                        the_item_sents.append(item)
                        break
            #print the_item_sents
            return the_item_sents
        except:
            print id_str, " ", domain
            return 

def prepareforannotate():
    bp = BlogProcessor()
    example_blogs_path = config.PROJECT_ROOT + 'analyze/use/'
    for (root, dirs, files) in os.walk(example_blogs_path):
        for i in files:
            t = i.split('.')
            print i
            tnd = t[0].split('_')
            fpath = os.path.join(example_blogs_path, i)
            items = bp.getcontent(tnd[1], tnd[0])
            f = open(fpath, 'a')
            f1 = open(fpath+'_rate', 'w')
            f.write('\n--------------------------------\n')
            for j in items:
                f.write(j.tostring())
                f1.write(j.content+'\n')
            f1.close()
            f.close()


def main(argv=None):
    bp = BlogProcessor()
    id_str = '184981932692619264'
    items = bp.getcontent(id_str, 'mashable')
    #for i in items:
        #print i.tostring()
    
    #prepareforannotate()

if __name__ == "__main__":
    sys.exit(main())
    
"""
    

        