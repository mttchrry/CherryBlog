# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="mcherry"
__date__ ="$Feb 4, 2014 3:19:28 PM$"

import cgi
import re
import random
import string
import time
import hashlib
import webapp2
from google.appengine.api import users
from google.appengine.ext import db
from BaseRenderingModule.BaseHandler import BaseHandler

def escape_html(s):
    return cgi.escape(s, quote=True)

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def create_cookie_hash(username, password, salt=""):
    if len(salt) == 0:
        salt = make_salt()
    h = hashlib.sha256(username + password + salt).hexdigest()
    return '%s_%s' % (h, salt)
    
def valid_pw(name, pw, h):
    key,salt = h.split('_')
    return h == create_cookie_hash(name, pw, salt)
    
class User(db.Model):
    username = db.StringProperty(required = True)
    password = db.StringProperty(required = True)  
    email = db.StringProperty(required = False)

class SignUpPage(BaseHandler):
    def get(self):
        self.render('SignUpHtml.html', **{"userName":"","nameError":"","passwordError":"",
                                 "verifyError":"","email":"","emailError":""})

    def post(self):
        user_username = self.request.get('username')
        user_password = self.request.get('password')
        user_verify = self.request.get('verify')
        user_email = self.request.get('email')

        usernameerror = ''
        passworderror = ''
        verifyerror = ''
        emailerror = ''

        valid_form = True

        if not valid_username(user_username):
            usernameerror = "That's not a valid username."
            valid_form = False
        else: 
            user=db.GqlQuery("Select * FROM User WHERE username = '%s'" % user_username)
            if user.count() > 0:
                usernameerror = "User Already Exists."
                valid_form = False
        if not valid_password(user_password):
            passworderror = "That is not a valid password."
            valid_form = False
        elif user_password != user_verify:
            verifyerror = "Passwords don't match"
            valid_form = False
        if len(user_email) > 0 and not valid_email(user_email):
            emailerror = "Invalid email"
            valid_form = False

        username = escape_html(user_username)
        if valid_form == False:
            email = escape_html(user_email)
            self.render('SignUpHtml.html', **{"userName":username,"nameError":usernameerror,"passwordError":passworderror,
                                     "verifyError":verifyerror,"email":email,"emailError":emailerror})
        else:
            user=User(username=username, password=user_password, email=user_email)
            user.put()
            hash = create_cookie_hash(username, user_password)
            self.response.headers.add_header('Set-Cookie', "user_id=%s|%s; Path=/"%(str(user.key().id()), hash))
            self.redirect("/blog/welcome")

class Login(BaseHandler):
    def get(self):
        self.render('Login.html', **{"userName":"","invalid":""})

    def post(self):
        user_username = self.request.get('username')
        user_password = self.request.get('password')

        valid_form = True
        invalid_msg = "Invalid username and password"
        
        if not valid_username(user_username):
            valid_form = False
        else: 
            user=db.GqlQuery("Select * FROM User WHERE username = '%s'" % user_username)
            if user.count() == 0:
                valid_form = False
            else:
                if not user[0].password == user_password:
                    valid_form=False
                    
        if valid_form:
            hash = create_cookie_hash(user_username, user_password)
            self.response.headers.add_header('Set-Cookie', "user_id=%s|%s; Path=/"%(str(user[0].key().id()), hash))
            self.redirect('/blog/welcome')
        else:
            username = escape_html(user_username)
            self.render('Login.html', **{"userName":username,"invalid":invalid_msg})
            
class Logout(BaseHandler):
     def get(self):
        self.response.delete_cookie('user_id')
        self.redirect('/blog/signup')
        #self.response.out.write("YouSignedOut")
        
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")

def valid_username(username):
    return USER_RE.match(username)

PASSWORD_RE = re.compile(r"^.{3,20}$")

def valid_password(password):
    return PASSWORD_RE.match(password)    

EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

def valid_email(email):
    return EMAIL_RE.match(email)

class Welcome(BaseHandler):
    def get(self):
        time.sleep(.5)
        user_id = self.get_user() #userCookie = self.request.cookies.get('user_id')
        if user_id:
            users = db.GqlQuery("SELECT * FROM User WHERE __key__ = KEY('User', %s)" % int(user_id))
            if users:
                self.response.out.write("Welcome, you signed up correctly %s"% users[0].username)
            else: 
                self.redirect("/blog/signup")
        else:
            self.redirect("/blog/signup") 
        
################################################
# Blog Stuff
################################################
class BlogPost(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)  
    created = db.DateTimeProperty(auto_now_add = True)
    modified = db.DateTimeProperty(auto_now = True)
    user = db.StringProperty(required = False)
    def to_dict(self):
       return dict([(p, unicode(getattr(self, p))) for p in self.properties()])
    
    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
 
class Blog(BaseHandler):
    def render_front(self):
        posts=db.GqlQuery("Select * FROM BlogPost ORDER BY created DESC LIMIT 10")
        user_id = self.get_user()
        self.render('BlogFrontPage.html', posts=posts, user=user_id)
    
    def get_json(self):
        return posts;
    
    def get(self):
        self.render_front()
            
class Newpost(BaseHandler):
        
    def get(self):
        self.render('Newpost.html')
    def post(self):
        title=self.request.get('subject')
        content=self.request.get('content')
        
        if content and title:
            time.sleep(.1)
            safe_title = escape_html(title)
            safe_content = escape_html(content)
            post = BlogPost(subject=safe_title, content=safe_content)
            post_key = post.put()
            self.redirect("/blog/%s" % post_key.id())
        else:
            error = "We need a title and content."
            self.render('Newpost.html', title=title, content=content, content_error=error)
            
class PermalinkHandler(BaseHandler):
    def get(self, blog_id):
        singlePost = db.GqlQuery("Select * FROM BlogPost WHERE __key__ = KEY('BlogPost', %s)" % int(blog_id))
        #singlePost = BlogPost.get_by_id(int(blog_id))
        if not singlePost:
            self.error(404)
            return
        else:
            self.render('BlogFrontPage.html', posts=singlePost)
