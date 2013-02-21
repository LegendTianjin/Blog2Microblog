'''
Created on Mar 1, 2012
@author: vandana

BlogContent Module.
It collects data for the given links of particular blogs and creates a content repository based on the url
'''
import config
import os
import crawler
import json
import sys
import tarfile
import StringIO
from pymongo import Connection

class BlogContent:
    def __init__(self, path):
        self.linkspath = path
        self.datadir = config.PROJECT_ROOT + 'data/blogcontent/'
        dbConn = Connection("localhost", 27017)
        #self.db = dbConn.blogcontent
        self.db = dbConn.b2mb
        self.db.blogcontent.ensure_index('id_str', unique=True)
    
    def getcontent(self):
        for (root, dirs, files) in os.walk(self.linkspath):
            for file_t in files:
                if '.data' in file_t:
                    domain = file_t.split('_')[0]
                    #content was parsed, added because of errors during data collection
                    #if domain == 'mashable' or domain == "businessinsider" or domain == 'fakingnews' or domain == "engadget" or domain == "nytimes" or domain == "huffingtonpost" or domain == "techcrunch":
                    #    continue
                    tar = tarfile.open(self.datadir+domain+'.tar.gz', 'w:gz')
                    
                    '''Code for data recovery '''
                    #tar = tarfile.open(self.datadir+domain+'.tar.gz', 'r:gz')
                    '''---------------'''
                    
                    f = open(os.path.join(root, file_t), 'r')
                    c = 0
                    for line in f:
                        c += 1
                        line = json.loads(line)
                        self.scrapeblog(line, domain, tar)
                        
                        if c > 400:
                            break
                        
                    tar.close()
            break
                
    def scrapeblog(self, tweet, domain, tar):
        url = tweet['entities']['urls'][0]['expanded_url']
        #print url
        """
        ''' Code for data recovery '''
        try:
            print tweet['id_str']
            fname = tweet['id_str']+".html"
            tar.extract(fname, self.datadir)
        except:
            print 'tar extract failed'
            return
        ''' ----- '''
        """
        
        bloghtml = crawler.Crawler.crawl(url, domain, tweet['id_str'], self.datadir)
        dbdoc = {}
        dbdoc['id_str'] = tweet['id_str']
        dbdoc['tweethandle'] = domain
        dbdoc['url'] = bloghtml.url
        if hasattr(bloghtml, 'body'): 
            dbdoc['body'] = bloghtml.body
            print dbdoc['body']
        else: dbdoc['body'] = ""
        if hasattr(bloghtml, 'comments'): dbdoc['comments'] = bloghtml.comments
        else: dbdoc['comments'] = ""
        if hasattr(bloghtml, 'title'): dbdoc['title'] = bloghtml.title
        else: dbdoc['title'] = ""
        if hasattr(bloghtml, 'blogparas'):
            dbdoc['paras'] = bloghtml.blogparas
            print dbdoc['paras']
        else: dbdoc['paras'] = ""
        if hasattr(bloghtml, 'html'):
            d1 = StringIO.StringIO(bloghtml.html) 
            info = tar.tarinfo()
            info.name = tweet['id_str'] + '.html'
            info.uname = 'vandana'
            info.gname = 'users'
            info.size = d1.len
            tar.addfile(info, d1)
        self.db.blogcontent.insert(dbdoc)
        """
        ''' Code for data recovery '''
        if fname:
            os.remove(self.datadir+fname)
        ''' -------------------- '''
        """
        
def main(argv=None):
    bc = BlogContent(config.PROJECT_ROOT + 'data/')
    bc.getcontent()

if __name__ == "__main__":
    sys.exit(main())