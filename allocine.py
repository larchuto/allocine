#! /usr/bin/env python
# -*- coding: utf8 -*-

import time
import base64
import hashlib
import urllib
import json


class allocineRequest():
    def __init__(self):
        self.secretKey = '29d185d98c984a359e6e6f26a0474269'
        self.partnerKey = '100043982026'
        self.route = ''
        self.tokens = {'format':'json', 'partner':self.partnerKey}

        self.decoder = json.JSONDecoder()
        self.result = ''
 
    def ksort(self, d):
        return [(k,d[k]) for k in sorted(d.keys())]
       
    def url(self):
        self.tokens['sed']     = time.strftime('%Y%m%d', time.localtime())
        self.tokens['sig']     = base64.b64encode(hashlib.sha1(self.secretKey + urllib.urlencode(self.ksort(self.tokens))).digest())
      
        return 'http://api.allocine.fr/rest/v3/' + self.route + '?' + urllib.urlencode(self.ksort(self.tokens))

    def send(self):
        opener = urllib.URLopener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        u = self.url()
        print u
        link = None
        # Sometimes the url open can fail.
        while link == None:
            try:
                link = opener.open(u)
            except IOError:
                print 'oo...an error'
        return link.read()
    
    def found(self):
        return (self.result != '')

    
class allocineSearch(allocineRequest):
    def __init__(self, q, filter='movie'):
        allocineRequest.__init__(self)
        self.route = 'search'


        self.q = q
        self.filter = filter
        self.search(self.q, filter)
        
    def search(self, title, filter):
        self.tokens['q'] = title
        self.tokens['filter'] = filter

        self.result = self.send()
        if self.result:
            try:
                self.result = self.decoder.decode(self.result)
            except:
                self.result = None

    def found(self):
        return (self.result != None) and (self.result['feed']['totalResults'] != 0)


class allocineMovie(allocineRequest):
    def __init__(self, code):
        allocineRequest.__init__(self)
        self.route = 'movie'
        self.code = code
        self.search(self.code)
 
    def search(self, code, filter='movie'):
        self.tokens['code'] = code
        self.tokens['filter'] = filter
        self.tokens['profile'] = 'large'
        self.tokens['striptags'] = 'synopsis'
        
        self.result = self.send()
        if self.result:
            try:
                self.result= self.decoder.decode(self.result)
            except:
                self.result = None

if __name__ == '__main__':
    s = allocineSearch("The place beyond the pines")
    if s.found():    
        for movie in s.result['feed']['movie']:
            print '%s - %d' % (movie['originalTitle'], movie['code'])

    m = allocineMovie(s.result['feed']['movie'][0]['code'])
    print m.result
        
    print '\n'
    print 'Genre : '
    print m.result['movie']['genre']
    print 'Synopsis : '
    print m.result['movie']['synopsis']
    print 'Realisateur'
    print m.result['movie']['castingShort']['directors']
    print 'Acteurs'
    try:
        print m.result['movie']['castingShort']['actors']
    except:
        print 'oups'
    print 'User rating'
    print m.result['movie']['statistics']['userRating']

    for k, v in m.result['movie'].iteritems():
        print k


'''
References :
    API : http://wiki.gromez.fr/dev/api/allocine_v3
    forum : http://fr.openclassrooms.com/forum/sujet/probleme-avec-l-api-d-allocine
'''
