#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import cgi
import re
import random
import string
import time
import hashlib
import webapp2

from google.appengine.api import users
from google.appengine.ext import db
from APIProvider import ApiProvider
from BaseRenderingModule.BaseHandler import BaseHandler
from Blog.Blog import Blog
from Blog.Blog import BlogPost
from Blog.Blog import Welcome
from Blog.Blog import SignUpPage
from Blog.Blog import PermalinkHandler
from Blog.Blog import Login
from Blog.Blog import Newpost
from Blog.Blog import Login
from Blog.Blog import Logout
from Blog.Blog import FlushCache
from Blog.Blog import EditPost

rot13Form = """
<form method="post">
    <textarea name="text" style="height: 100px; width: 400px;">%(rotText)s</textarea>
    <br>
    <input type="submit">
</form>
"""


def escape_html(s):
    return cgi.escape(s, quote=True)


def all_letters(begin='a', end='z'):
    beginNum = ord(begin)
    endNum = ord(end)
    for number in (xrange(beginNum, endNum + 1)):
    #xrange(BeginNum, EndNum + 1))):
        yield chr(number)
        yield chr(number).upper()
    
class MainPage(BaseHandler):
    def write_form(self, rotText=""):
        self.response.out.write(rot13Form % {"rotText": rotText})

    def get(self):
        self.write_form()

    def post(self):
        rotText = 'a'
        user_Rot = self.request.get('text')
        if user_Rot:
            rotText = user_Rot
            #rotText = user_Rot.encode('rot13')
        rottedText = ''
        for i in range(0, len(rotText)): #= 0; i<RotText.length; i++) in RotText[i]:
            if rotText[i] in ''.join(all_letters()):
                c = rotText[i].lower()
                if c < 'n':
                    rottedText += chr(ord(rotText[i]) + 13)
                else:
                    rottedText += chr(ord(rotText[i]) - 13)
            else:
                rottedText += rotText[i]
        cleanRotted = escape_html(rottedText)
        self.write_form(cleanRotted)

secretHash="mySecret"

class DeletePosts(BaseHandler):
    def get(self):
        query = BlogPost.all(keys_only=True)
        entries = query.fetch(1000)
        db.delete(entries)
        self.write("All posts have been removed")
################################################
# Web Directs
################################################
app = webapp2.WSGIApplication([
                                  ('/', MainPage),
                                  ('/blog/signup', SignUpPage),
                                  ('/blog/welcome', Welcome),
                                  ('/blog/?', Blog),
                                  ('/blog/edit/([0-9]+)', EditPost),
                                  ('/blog/newpost', Newpost),
                                  ('/blog/([0-9]+)', PermalinkHandler),
                                  ('/blog/login', Login),
                                  ('/blog/logout', Logout),
                                  ('/blog/?(.*).json', ApiProvider),
                                  ('/blog/removeallposts', DeletePosts),
                                  ('/blog/flush', FlushCache)                        
                              ], debug=True)


