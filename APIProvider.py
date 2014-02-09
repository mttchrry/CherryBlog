# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="mcherry"
__date__ ="$Feb 4, 2014 11:44:12 AM$"

from BaseRenderingModule.BaseHandler import BaseHandler
from Blog.Blog import Blog
from Blog.Blog import BlogPost
import re
import json
from google.appengine.api import users
from google.appengine.ext import db


class ApiProvider(BaseHandler):
    def get(self, pathargs):
        self.response.headers["Content-Type"] = 'application/json; charset=UTF-8'
        blogPath = pathargs.replace('/','')
        blogID = re.compile(r"^[0-9]+$")
        if blogID.match(blogPath):
            singlePost = db.GqlQuery("Select * FROM BlogPost WHERE __key__ = KEY('BlogPost', %s)" % int(blogPath))
            self.write(json.dumps([p.to_dict() for p in singlePost]))
        elif len(pathargs) == 0:
            posts = db.GqlQuery("Select * FROM BlogPost")
            self.write(json.dumps([p.to_dict() for p in posts]))
        else:
            self.error(404)
            return