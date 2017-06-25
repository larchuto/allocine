#! /usr/bin/env python
# -*  coding: utf8 -*-

import sys
import time
import base64
import hashlib
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json


'''
References :
    API : http://wiki.gromez.fr/dev/api/allocine_v3
    forum : http://fr.openclassrooms.com/forum/sujet/probleme-avec-l-api-d-allocine
'''


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
        param_str              = self.secretKey + urlencode(self.ksort(self.tokens))
        self.tokens['sig']     = base64.b64encode(hashlib.sha1(param_str.encode()).digest())
      
        return 'http://api.allocine.fr/rest/v3/' + self.route + '?' + urlencode(self.ksort(self.tokens))

    def send(self):
        request = Request(self.url())
        request.add_header('User-agent','Mozilla/5.0')
        link = None
        # Sometimes the url open can fail.
        while link == None:
            try:
                link = urlopen(request)
            except IOError:
                print('oo...an error')
        return link.read().decode()
    
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
    from textwrap import wrap
    import subprocess
    import datetime

    def usage():
        print('''
    allocine.py title
    =================

        This is actually just an example of use of this allocine library
        Updates that construct web page for example will happen soon

          title : Title or part

        ''')

    def print_data(data_name, data_expr, column_size=80):
        try:
            data = str(eval(data_expr))
            wrapped_data = wrap(data, width = int(column_size) - len(data_name),
                                      initial_indent    = '\t' + ' '*len(data_name),
                                      subsequent_indent = '\t' + ' '*len(data_name))
            print(wrapped_data[0], end='')
            print("\r\t%s" % data_name)
            for i in range(1,len(wrapped_data)):
                print(wrapped_data[i])
        except KeyError:
            pass

    # get terminal size
    rows, columns = subprocess.check_output(['stty', 'size']).decode().split()

    if len(sys.argv) < 2:
        usage()
    else:
        s = allocineSearch(sys.argv[1])
        if s.found():
            i = 0
            for unit_result in s.result['feed']['movie']:
                i = i+1
                result_title = "Result %d" % i
                print(result_title)
                print("="*len(result_title))
                code = unit_result['code']
                movie=allocineMovie(code).result['movie']
                print_data("title            ", "movie['title']"                                       , columns)
                # print_data("original title   ", "movie['originalTitle']"                               , columns)
                print_data("year             ", "movie['productionYear']"                              , columns)
                print_data("director(s)      ", "movie['castingShort']['directors']"                   , columns)
                print_data("actors           ", "movie['castingShort']['actors']"                      , columns)
                print_data("genre            ", "', '.join([genre['$'] for genre in movie['genre']])"  , columns)
                print_data("nationality      ", "', '.join([nat['$'] for nat in movie['nationality']])", columns)
                print_data("runtime          ", "str(datetime.timedelta(seconds=movie['runtime']))"                                     , columns)
                print_data("synopsis         ", "movie['synopsis']"                                    , columns)
                # print_data("allocine url     ", "movie['link'][0]['href']"                             , columns)
                # print_data("poster url       ", "movie['poster']['href']"                              , columns)
                print()
