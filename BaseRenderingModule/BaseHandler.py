# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

import webapp2
import jinja2
import os
import urllib
import hashlib
#from Blog.Blog import User
from google.appengine.api import users
from google.appengine.ext import db

def create_cookie_hash(username, password, salt=""):
    if len(salt) == 0:
        salt = make_salt()
    h = hashlib.sha256(username + password + salt).hexdigest()
    return '%s_%s' % (h, salt)
    
def valid_pw(name, pw, h):
    key,salt = h.split('_')
    return h == create_cookie_hash(name, pw, salt)

#template_dir = os.path.join(os.path.dirname(__file__), 'Templates')
template_dir = os.path.join(os.path.abspath(''), 'Templates')

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    extensions=['jinja2.ext.autoescape'],
    autoescape = True)

class BaseHandler(webapp2.RequestHandler):
    def render_str(self, template, **params):
        t=jinja_env.get_template(template)
        return t.render(params)    
    
    def render(self, template, **kw):
        self.response.out.write(self.render_str(template, **kw))
    
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
    def get_user(self):
        userCookie = self.request.cookies.get('user_id')
        if userCookie:
            user_id, hash_val = userCookie.split("|")
            users = db.GqlQuery("SELECT * FROM User WHERE __key__ = KEY('User', %s)" % int(user_id))
            if users:
                if valid_pw(users[0].username, users[0].password, hash_val):
                    return user_id 
                else: 
                    return none
   