'''
Created on Feb 26, 2012
@author: vandana
'''
import re
import sys
import urllib
import json
from urlexpander import expandURL
#import spynner

from BeautifulSoup import BeautifulSoup
import httplib2
        
class Crawler:
    @staticmethod
    def crawl(url, domain, tweetid=None, path=None):
        return BlogHtml(url, domain, tweetid, path)

class BlogHtml:
    #BLOG_TYPES = ['engadget', 'techcrunch', 'nytimes', 'mashable', 'businessinsider', 'fakingnews', 'espn', 'foxsports', 'huffingtonpost', 'treehugger']
    def __init__(self, url=None, domain=None, tweetid=None, path=None):
        if url:
            self.domain = domain
            self.url = url
            if path:
                self.blogcontentpath = path
            if tweetid:
                self.tweetid = tweetid 
            func = getattr(self, "get" + domain)
            if func:
                func(url)

    def gettitle(self):
        if not self.soup or not self.soup.html:
            return ""
        titletag = self.soup.html.head.title
        return titletag.string
    
    def getengadget(self, url):
        http = httplib2.Http()
        (header, pagehtml) = http.request(url, 'GET')
        """
        ''' Code for recovery '''
        htmlfile = open(self.blogcontentpath+self.tweetid+".html", 'r')
        pagehtml = ""
        if htmlfile:
            pagehtml = "".join(htmlfile.readlines())
        '''-------------------------'''
        """
        bs = BeautifulSoup(pagehtml)
        self.html = pagehtml
        self.url = url
        self.soup = bs
        self.soup.prettify()
        self.title = self.gettitle()
        self.comments = self.getcomments()
        
        """
        x = self.soup.findAll('div', attrs={'class':'post_body'})
        if type(x) is list:
            body = x[0].contents
        elif x:
            body = x
        else:
        """  
        try: 
            body = self.soup.findAll('div', attrs={'class':'post_body'})[0].contents
            body = body[2:len(body)-4]
            blogdata = ""
            blogdata = self.getdata(body, blogdata)
            blogparas = ""
            blogparas = self.getparas(body)
            self.body = blogdata
            self.blogparas = blogparas
            print blogdata
        except:
            print "body not initialized: ", url
            return
    
    def getnytimes(self, url):
        community_key = '35fb5c7778409b89b6869e2ac8f79838:0:65748530'
        article_key = '8870ced3a7299320d2efd36791e636c8:5:65748530'
        expanded_content = expandURL(url)
        self.url = exp_url = re.sub(r'(http://www)\d*(\..*)\?.*', r'\1\2', expanded_content['long-url'])
        q = 'url:' + '"' + exp_url + '"'
        article_api_query = 'http://api.nytimes.com/svc/search/v1/article?format=json&query={0}&api-key={1}'.format(urllib.quote_plus(q), urllib.quote_plus(article_key))
        http = httplib2.Http()
        
        (response, content) = http.request(article_api_query, 'GET')
        try:
            if response['status'] == '200':
                content = json.loads(content)
                self.body = content['results'][0]["body"]
                print self.body
        except:
            print "body not initialized: ", self.url
        
        try:
            #redirection failure
            (res1, cont1) = http.request(exp_url, 'GET')
            if res1['status'] == '200':
                print cont1
        except:
            print 'could not get data by crawling', exp_url
        
        comm_api_query = 'http://api.nytimes.com/svc/community/v2/comments/url/exact-match.json?&url={0}&api-key={1}'.format(urllib.quote_plus(exp_url), urllib.quote_plus(community_key))
        (response, content) = http.request(comm_api_query, 'GET')
        if response['status'] == '200':
            content = json.loads(content)
            self.comments = content['results']['comments'] 
    
    def getmashable(self, url):
        http = httplib2.Http()
        (header, pagehtml) = http.request(url, 'GET')
        """
        ''' Code for recovery '''
        htmlfile = open(self.blogcontentpath+self.tweetid+".html", 'r')
        pagehtml = ""
        if htmlfile:
            pagehtml = "".join(htmlfile.readlines())
            header = {'status':'200'}
        else:
            print 'error getting html for', self.tweetid, " ", self.url
            
        '''-------------------------'''
        """
        if header['status'] == '200':
            bs = BeautifulSoup(pagehtml)
            self.html = pagehtml
            self.url = url
            self.soup = bs
            self.soup.prettify()
            self.title = self.gettitle()
            
            try:
                body = self.soup.findAll('div', attrs={'class':'description'})
                blogdata = ""
                blogdata = self.getdata(body, blogdata)
                self.body = blogdata
                blogparas = ""
                blogparas = self.getparas(body)
                self.blogparas = blogparas
                
                comments = self.soup.findAll('div', attrs={'class':'comment-body'})
                cc = []
                for i in comments:
                    cdata = ""
                    cdata = self.getdata(i, cdata)
                    cc.append(cdata)
                self.comments = cc
            except:
                print "body not initialized: ", url
                return
            
    def gettechcrunch(self, url):
        http = httplib2.Http()
        (header, pagehtml) = http.request(url, 'GET')
        """
        ''' Code for recovery '''
        htmlfile = open(self.blogcontentpath+self.tweetid+".html", 'r')
        pagehtml = ""
        if htmlfile:
            pagehtml = "".join(htmlfile.readlines())
            header = {'status':'200'}
        else:
            print 'error getting html for', self.tweetid, " ", self.url
            
        '''-------------------------'''
        """
        if header['status'] == '200':
            bs = BeautifulSoup(pagehtml)
            self.html = pagehtml
            self.url = url
            self.soup = bs
            self.soup.prettify()
            self.title = self.gettitle()
            
            try:
                bodys = self.soup.findAll('div', attrs={'class':'body-copy'})
                self.body = ""
                self.blogparas = []
                body = bodys[0].contents
                #body = self.soup.findAll('div', attrs={'class':'body-copy'})[0].contents
                blogdata = ""
                blogdata = self.getdata(body, blogdata)
                self.body += blogdata
                blogparas = ""
                blogparas = self.getparas(body)
                self.blogparas.extend(blogparas)
                #print blogdata
            except:
                print "body not initialized", url
                return
    
    def gettreehugger(self, url):
        http = httplib2.Http()
        try:
            (header, pagehtml) = http.request(url, 'GET')
        except:
            print "url error"
            return
        """
        ''' Code for recovery '''
        htmlfile = open(self.blogcontentpath+self.tweetid+".html", 'r')
        pagehtml = ""
        if htmlfile:
            pagehtml = "".join(htmlfile.readlines())
            header = {'status':'200'}
        else:
            print 'error getting html for', self.tweetid, " ", self.url
            
        '''-------------------------'''
        """
        if header['status'] == '200':
            bs = BeautifulSoup(pagehtml)
            self.html = pagehtml
            self.url = url
            self.soup = bs
            self.soup.prettify()
            self.title = self.gettitle()
            
            try:
                body = self.soup.findAll('div', attrs={'id':'entry-body'})[0].contents
                blogdata = ""
                blogdata = self.getdata(body, blogdata)
                self.body = blogdata
                blogparas = ""
                blogparas = self.getparas(body)
                self.blogparas = blogparas
            except:
                print "body not initialized", url
                return
    
    def getcnetnews(self, url):
        url = url.strip('\n')
        http = httplib2.Http()
        try:
            (header, pagehtml) = http.request(url, 'GET')
        except:
            print "url error"
            return
        if header['status'] == '200':
            bs = BeautifulSoup(pagehtml)
            self.html = pagehtml
            self.url = url
            self.soup = bs
            self.soup.prettify()
            self.title = self.gettitle()
            
            try:
                body = self.soup.findAll('div', attrs={'class':'post'})[0].contents
                blogdata = ""
                blogdata = self.getdata(body, blogdata)
                self.body = blogdata
                blogparas = ""
                blogparas = self.getparas(body)
                self.blogparas = blogparas
            except:
                print "body not initialized", url
                return
    
    def gethuffingtonpost(self, url):
        http = httplib2.Http()
        try:
            """
            ''' Code for recovery '''
            htmlfile = open(self.blogcontentpath+self.tweetid+".html", 'r')
            pagehtml = ""
            if htmlfile:
                pagehtml = "".join(htmlfile.readlines())
                header = {'status':'200'}
            else:
                print 'error getting html for', self.tweetid, " ", self.url
                
            '''-------------------------'''
            """
            (header, pagehtml) = http.request(url, 'GET')
            if header['status'] == '200':
                bs = BeautifulSoup(pagehtml)
                self.html = pagehtml
                self.url = url
                self.soup = bs
                self.soup.prettify()
                self.title = self.gettitle()
            
            
                body = self.soup.findAll('div', attrs={'class':'entry_body_text'})[0].contents
                #body = self.soup.findAll('div', attrs={'class':'text'})[0].contents
                body = body[3:len(body)-10]
                blogdata = ""
                blogdata = self.getdata(body, blogdata)
                self.body = blogdata
                blogparas = ""
                blogparas = self.getparas(body)
                self.blogparas = blogparas
        except:
            print "body not initialized", url
            return
            """
            bdata = re.sub(r'(.*)ShareShareDigg.*', r'\1', blogdata)
            m = re.search('(?<=//-->).*', blogdata)
            self.body = bdata
            print bdata
            
            self.comments = m.group(0)
            """
    
    def getespn(self, url):
        return ""
    
    def getfakingnews(self, url):
        http = httplib2.Http()
        (header, pagehtml) = http.request(url, 'GET')
        """
        ''' Code for recovery '''
        try:
            htmlfile = open(self.blogcontentpath+self.tweetid+".html", 'r')
            pagehtml = ""
            if htmlfile:
                pagehtml = "".join(htmlfile.readlines())
                header = {'status':'200'}
            else:
                print 'error getting html for', self.tweetid, " ", self.url
        except:
            return
            
        '''-------------------------'''
        """
        if header['status'] == '200':
            bs = BeautifulSoup(pagehtml)
            self.html = pagehtml
            self.url = url
            self.soup = bs
            self.soup.prettify()
            self.title = self.gettitle()
            
            try:
                x = self.soup.findAll('div', attrs={'id':'innerContent'})
                if type(x) is list:
                    body = x[0].contents
                elif x:
                    body = x
                else:
                    print "body not initialized: ", url
                    return
                #body = self.soup.findAll('div', attrs={'id':'innerContent'})[0].contents
                blogdata = ""
                blogdata = self.getdata(body, blogdata)
                bdata = re.sub(r'(.*)ShareShareDigg.*', r'\1', blogdata)
                m = re.search('(?<=//-->).*', blogdata)
                self.body = bdata
                print bdata
                self.comments = m.group(0)
                blogparas = ""
                blogparas = self.getparas(body)
                self.blogparas = blogparas
            except:
                print 'body not initialized', url
                return
    
    def getbusinessinsider(self, url):
        http = httplib2.Http()
        (header, pagehtml) = http.request(url, 'GET')
        """
        ''' Code for recovery '''
        try:
            htmlfile = open(self.blogcontentpath+self.tweetid+".html", 'r')
            pagehtml = ""
            if htmlfile:
                pagehtml = "".join(htmlfile.readlines())
                header = {'status':'200'}
            else:
                print 'error getting html for', self.tweetid, " ", self.url
        except:
            return
            
        '''-------------------------'''
        """
        if header['status'] == '200':
            bs = BeautifulSoup(pagehtml)
            self.html = pagehtml
            self.url = url
            self.soup = bs
            self.soup.prettify()
            self.title = self.gettitle()
            try:
                x = self.soup.findAll('div', attrs={'class':'KonaBody post-content'})
                if type(x) is list:
                    body = x[0].contents
                    body = body[1:len(body)]
                elif x:
                    body = x
                else:
                    print "body not initialized: ", url
                    return
                blogdata = ""
                blogdata = self.getdata(body, blogdata)
                self.body = blogdata
                blogparas = ""
                blogparas = self.getparas(body)
                self.blogparas = blogparas
            except:
                print "body not initialized: ", url
                return
    
    def getndtv(self, url):
        http = httplib2.Http()
        (header, pagehtml) = http.request(url, 'GET')
        if header['status'] == '200':
            bs = BeautifulSoup(pagehtml)
            self.html = pagehtml
            self.url = url
            self.soup = bs
            self.soup.prettify()
            self.title = self.gettitle()
            try:
                x = self.soup.findAll('div', attrs={'class':'itemFullText'})
                if not x:
                    x = self.soup.findAll('div', attrs={'id':'storycontent'})
                if type(x) is list:
                    body = x[0].contents
                    body = body[1:len(body)]
                elif x:
                    body = x
                else:
                    print "body not initialized: ", url
                    return
                blogdata = ""
                blogdata = self.getdata(body, blogdata)
                self.body = blogdata
                blogparas = ""
                blogparas = self.getparas(body)
                self.blogparas = blogparas
            except:
                print "body not initialized: ", url
                return
    
    def getcontentparas(self, html, domain):
        bs = BeautifulSoup(html)
        bs.prettify()
        body = []
        try:
            if domain == "engadget":
                body = bs.findAll('div', attrs={'class':'post_body'})[0].contents
                body = body[2:len(body)-4]
            elif domain == "mashable":
                body = bs.findAll('div', attrs={'class':'description'})
            elif domain == "techcrunch":
                body = bs.findAll('div', attrs={'class':'body-copy'})[0].contents
            elif domain == "huffingtonpost":
                body = bs.findAll('div', attrs={'class':'entry_body_text'})[0].contents
                body = body[3:len(body)-10]
            elif domain == "treehugger":
                body = bs.findAll('div', attrs={'id':'entry-body'})[0].contents
            elif domain == "businessinsider":
                x = bs.findAll('div', attrs={'class':'KonaBody post-content'})
                if type(x) is list:
                    body = x[0].contents
                    body = body[1:len(body)]
                elif x:
                    body = x
                else:
                    print "body not initialized: "
            #print body
            blogparas = ""
            blogparas = self.getparas(body)
            return blogparas
        except:
            print "para not found: "
            return "0"

    def getparas(self, body):
        paras = []
        for i in body:
            #bs = BeautifulSoup(i)
            if not hasattr(i, 'findAll'):
                continue
            if self.domain == 'ndtv':
                parahtmls = i.findAll(text=True)
                for j in parahtmls:
                    if j  and j.strip() != "":
                        paras.append(j.strip())
            else:
                if i.name == 'p':
                    parahtmls = [i]
                else:
                    parahtmls = i.findAll('p')
                for j in parahtmls:
                    paracontent = ""
                    paracontent = self.getdata(j, paracontent)
                    if paracontent and paracontent.strip() != " ":
                        paras.append(paracontent.strip())
        #print paras
        return paras
    
    def getdata(self, body, blogdata):
        for i in body:
            blogdata = self.getdatarecur(i, blogdata)
            blogdata = blogdata + " "
        return blogdata
        
    def getdatarecur(self, tag, blogdata):
        if not tag:
            return ""
        if tag.string == None:
            if tag.contents == None:
                blogdata = blogdata + tag
            else:
                for i in tag.contents:
                    blogdata = self.getdatarecur(i, blogdata)
        else:
            blogdata = blogdata + tag.string
        return blogdata
            
    def getcomments(self):
        return ""

def main(argv=None):
    #url = 'http://www.engadget.com/2012/02/26/viewsonic-viewphone-4s-hands-on-video/?utm_source=twitterfeed&utm_medium=twitter'
    #url = 'http://techcrunch.com/2012/02/26/tcmwc-hands-on-with-the-htc-one-s/'
    #Crawler.crawl(url, None, None)
    #html = Crawler.html
    #url = 'http://nyti.ms/z2IJQt'
    #url = 'http://www.fakingnews.com/2012/03/government-aks-google-to-disclose-the-number-of-gays-in-india/'
    #url = 'http://www.fakingnews.com/2012/02/bcci-drops-non-performing-poonam-pandey-from-asia-cup/'
    url = 'http://huff.to/Ary9iP'
    #url = 'http://on.mash.to/wwSAQW'
    #url = 'http://t.co/xy6IvDbA'
    #url = 'http://read.bi/zYTbCc'
    #url = 'http://tcrn.ch/A3Srdd'
    #url = 'http://www.businessinsider.com/barack-obama-just-went-after-the-wealthy-libertarian-koch-brothers-on-his-twitter-account-2012-2'
    #b = BlogHtml(url, 'businessinsider')
    #b = BlogHtml(url, 'nytimes')
    #url = 'http://t.co/R9cukdpi'
    #url = 'http://www.ndtv.com/article/world/mumbai-miami-on-list-for-big-weather-disasters-191150'
    b = BlogHtml(url, 'huffingtonpost')

if __name__ == "__main__":
    sys.exit(main())        